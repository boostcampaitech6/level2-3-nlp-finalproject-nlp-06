import argparse
import transformers
import torch
import random
from tqdm.auto import tqdm
import pandas as pd
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu
import re
import json
import os

import pytorch_lightning as pl
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import WandbLogger
import wandb

############################################### Dataset ###############################################
class Dataset(torch.utils.data.Dataset):
    def __init__(self, encoder_inputs, decoder_inputs, decoder_targets):
        self.encoder_inputs = encoder_inputs
        self.decoder_inputs = decoder_inputs
        self.decoder_targets = decoder_targets

    def __getitem__(self, idx):
        return {"encoder_input_ids" : self.encoder_inputs['input_ids'][idx], 
                "encoder_attention_mask" : self.encoder_inputs['attention_mask'][idx],
                "decoder_input_ids" : self.decoder_inputs['input_ids'][idx],
                "decoder_input_attention_mask" : self.decoder_inputs['attention_mask'][idx],
                "decoder_target_ids" : self.decoder_targets['input_ids'][idx]}
    def __len__(self):
        return len(self.encoder_inputs['input_ids'])
    
############################################### Dataloader ###############################################
class Dataloader(pl.LightningDataModule):
    def __init__(self, model_name, batch_size, shuffle, train_path, val_path, test_path, predict_path):
        super().__init__()
        self.model_name = model_name
        self.batch_size = batch_size
        self.shuffle = shuffle
        
        self.train_path = train_path
        self.val_path = val_path
        self.test_path = test_path
        self.predict_path = predict_path

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.model_name)
        
        special_tokens_dict = {'additional_special_tokens': ['[BOS]', '[SEP]']}
        self.tokenizer.add_special_tokens(special_tokens_dict)
        self.tokenizer.add_special_tokens({'bos_token': '<s>'})

    def tokenizing(self, series, max_len):
        tokens = self.tokenizer(series.tolist(), padding='max_length', max_length=max_len ,return_tensors="pt", truncation=True)
        return tokens # input_ids, attention_mask

    def preprocessing(self,dataframe):
        # session_dialog_add_special_tokens
        dataframe['session_dialog'] = dataframe['session_dialog'].apply(lambda x: '[BOS] ' + ' [SEP] '.join(eval(x))) # ['A','B','C'] -> '[BOS] A [SEP] B [SEP] C [SEP] </s>'
        dataframe['session_persona'] = dataframe['session_persona'].apply(lambda x: '<s> '+','.join(eval(x)).replace('.','')+'.') # ['A.','B.','C.'] -> '<s> A,B,C. </s>'
        dataframe['session_persona_target'] =  dataframe['session_persona'].apply(lambda x: x[4:]) # <s> 제외

        # tokenizing
        encoder_inputs = self.tokenizing(dataframe['session_dialog'], max_len=500)
        decoder_inputs = self.tokenizing(dataframe['session_persona'], max_len=200)
        decoder_targets = self.tokenizing(dataframe['session_persona_target'], max_len=200)

        return encoder_inputs, decoder_inputs, decoder_targets

    def setup(self, stage='fit'):
        if stage == 'fit':
            train_df = pd.read_csv(self.train_path)
            val_df = pd.read_csv(self.val_path)

            train_encoder_inputs, train_decoder_inputs, train_decoder_targets = self.preprocessing(train_df)
            val_encoder_inputs, val_decoder_inputs, val_decoder_targets  = self.preprocessing(val_df)

            self.train_dataset = Dataset(train_encoder_inputs, train_decoder_inputs, train_decoder_targets)
            self.val_dataset = Dataset(val_encoder_inputs, val_decoder_inputs, val_decoder_targets)
        else:
            test_df = pd.read_csv(self.test_path)
            predict_df = pd.read_csv(self.predict_path)

            test_encoder_inputs, test_decoder_inputs, test_decoder_targets= self.preprocessing(test_df)
            predict_encoder_inputs, predict_decoder_inputs, perdict_decoder_targets = self.preprocessing(predict_df)

            self.test_dataset = Dataset(test_encoder_inputs, test_decoder_inputs, test_decoder_targets)
            self.predict_dataset = Dataset(predict_encoder_inputs, predict_decoder_inputs, perdict_decoder_targets)

    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=self.shuffle)
    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.val_dataset, batch_size=self.batch_size)
    def test_dataloader(self):
        return torch.utils.data.DataLoader(self.test_dataset, batch_size=self.batch_size)
    def predict_dataloader(self):
        return torch.utils.data.DataLoader(self.predict_dataset, batch_size=self.batch_size)
    

############################################### Model ###############################################
class Model(pl.LightningModule):
    def __init__(self, model_name, lr, tokenizer):
        super().__init__()
        self.save_hyperparameters()

        self.model = transformers.T5ForConditionalGeneration.from_pretrained(model_name, cache_dir='./model')
        self.model.config.decoder_start_token_id = tokenizer.bos_token_id
        self.model.resize_token_embeddings(len(tokenizer))

        self.tokenizer = tokenizer
        self.lr = lr

        self.loss = torch.nn.CrossEntropyLoss(ignore_index=self.tokenizer.pad_token_id)

    def compute_rouge_score(self, logits, target) -> dict:
        # logits : (batch_size, decoder_max_len, vocab_size)
        # target : (batch_size, decoder_max_len)
        rouge = Rouge()
        
        pred_strings = []
        target_strings = []

        pred_ids = torch.argmax(logits, dim=-1) # (batch_size, decoder_max_len)
        for batch in range(pred_ids.shape[0]):
            pred_string = re.findall(r'^.*(?=<\/s>)',self.tokenizer.decode(pred_ids[batch])) # truncate until </s>
            if pred_string:
                pred_string = pred_string[0].strip() if pred_string[0] else ' '
            else:
                pred_string = ' '
             
            target_string = self.tokenizer.decode(target[batch], skip_special_tokens=True)
            pred_strings.append(pred_string)
            target_strings.append(target_string)

        
        scores = rouge.get_scores(pred_strings, target_strings, avg=True)
        # f1, precision, recall
        # {'rouge-1': {'f': .., 'p': .., 'r': ..}, 
        # 'rouge-2': {'f': .., 'p': .., 'r': ..}, 
        # 'rouge-l': {'f': .., 'p': .., 'r': ..}}
        
        return scores 

    def compute_bleu_score(self, logits, target) -> float:
        # logits : (batch_size, decoder_max_len, vocab_size)
        # target : (batch_size, decoder_max_len)
        total_bleu_score = 0

        pred_ids = torch.argmax(logits, dim=-1)
        for batch in range(pred_ids.shape[0]):
            pred_string = re.findall(r'^.*(?=<\/s>)',self.tokenizer.decode(pred_ids[batch])) # truncate until </s>
            if pred_string:
                pred_string = pred_string[0].strip() if pred_string[0] else ' '
            else:
                pred_string = ' '
            
            target_string = self.tokenizer.decode(target[batch], skip_special_tokens=True).strip()
            
            total_bleu_score += sentence_bleu(target_string, pred_string, weights=(1, 0, 0, 0))

        return total_bleu_score / pred_ids.shape[0]

    def forward(self, **x):
        '''
        x = {"encoder_input_ids" : (batch_size, encoder_max_len),
             "encoder_attention_mask" : (batch_size, encoder_max_len),
             "decoder_input_ids" : (batch_size, decoder_max_len), # target 역할도 수행
             "decoder_input_attention_mask" : (batch_size, decoder_max_len)}
        '''

        outputs = self.model(input_ids=x['encoder_input_ids'], attention_mask=x['encoder_attention_mask'], 
                            decoder_input_ids=x['decoder_input_ids'], decoder_attention_mask=x['decoder_input_attention_mask'])
        
        return outputs
    
    def training_step(self, batch, batch_idx):
        
        outputs = self(**batch) # (batch_size, decoder_max_len, vocab_size)
        loss = self.loss(outputs.logits.view(-1, outputs.logits.shape[-1]), batch['decoder_target_ids'].view(-1)) # (batch_size*decoder_max_len, vocab_size), (batch_size*decoder_max_len)
        self.log("train_loss", loss)

        rouge_score = self.compute_rouge_score(outputs.logits, batch['decoder_target_ids'])
        bleu_score = self.compute_bleu_score(outputs.logits, batch['decoder_target_ids'])

        self.log_dict({"rouge-1-recall" : round(rouge_score['rouge-1']['r'],3),
                       "rouge-1-precision" : round(rouge_score['rouge-1']['p'],3),
                       "rouge-1-f1" : round(rouge_score['rouge-1']['f'],3)})
        self.log_dict({"rouge-2-recall" : round(rouge_score['rouge-2']['r'],3),
                        "rouge-2-precision" : round(rouge_score['rouge-2']['p'],3),
                        "rouge-2-f1" : round(rouge_score['rouge-2']['f'],3)})
        self.log_dict({"rouge-l-recall" : round(rouge_score['rouge-l']['r'],3),
                        "rouge-l-precision" : round(rouge_score['rouge-l']['p'],3),
                        "rouge-l-f1" : round(rouge_score['rouge-l']['f'],3)})
        self.log_dict({"bleu_avg" : round(bleu_score,3)})
        
        return loss
    
    def validation_step(self, batch, batch_idx):

        outputs = self(**batch)
        loss = self.loss(outputs.logits.view(-1, outputs.logits.shape[-1]), batch['decoder_input_ids'].view(-1))
        self.log("val_loss", loss)

        rouge_score = self.compute_rouge_score(outputs.logits, batch['decoder_target_ids'])
        bleu_score = self.compute_bleu_score(outputs.logits, batch['decoder_target_ids'])

        self.log_dict({"val_rouge-1-recall" : round(rouge_score['rouge-1']['r'],3),
                       "val_rouge-1-precision" : round(rouge_score['rouge-1']['p'],3),
                       "val_rouge-1-f1" : round(rouge_score['rouge-1']['f'],3)})
        self.log_dict({"val_rouge-2-recall" : round(rouge_score['rouge-2']['r'],3),
                        "val_rouge-2-precision" : round(rouge_score['rouge-2']['p'],3),
                        "val_rouge-2-f1" : round(rouge_score['rouge-2']['f'],3)})
        self.log_dict({"val_rouge-l-recall" : round(rouge_score['rouge-l']['r'],3),
                        "val_rouge-l-precision" : round(rouge_score['rouge-l']['p'],3),
                        "val_rouge-l-f1" : round(rouge_score['rouge-l']['f'],3)})
        self.log_dict({"val_bleu_avg" : round(bleu_score,3)})

        return loss

    def test_step(self, batch, batch_idx):
            
        outputs = self(**batch)
        loss = self.loss(outputs.logits.view(-1, outputs.logits.shape[-1]), batch['decoder_input_ids'].view(-1))
    
        return loss
    
    def predict_step(self, batch, batch_idx):

        outputs = self(**batch)
        return outputs.logits
    
    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer

############################################### Main ###############################################
def main():
    
    ## seed fix ##
    SEED= 42
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    random.seed(SEED)

    ## parser ##
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='et5/et5-banmal-by-rougel-f1-config.json')
    args = parser.parse_args()

    ## config ##
    selected_config = args.config

    with open(f'./configs/{selected_config}', 'r') as f:
        config = json.load(f)

    print('*****************************************************')
    print(f" config: '{args.config}' is loaded")
    print('*****************************************************')

    ## wandb logger ##
    wandb_logger = WandbLogger(project=config["wandb_project"], entity=config["wandb_entity"], name=config["wandb_run_name"])

    ## dataloader ##
    dataloader = Dataloader(config["model_name"],config["batch_size"],
                            config["shuffle"], config["train_path"], config["dev_path"],
                            config["test_path"], config["predict_path"])
    
    ## model ##
    model = Model(config["model_name"], config["learning_rate"], dataloader.tokenizer)

    ## callbacks ##
    early_stop_custom_callback = EarlyStopping(
        config['metric'], patience=3, verbose=True, mode="max"
    )

    checkpoint_callback = ModelCheckpoint(
        monitor=config['metric'],
        save_top_k=1,
        dirpath="./checkpoints/",
        filename=config["model_detail"], # model에 따라 변화
        save_weights_only=False,
        verbose=True,
        mode=config['metric_mode'],
    )

    ## trainer ##
    trainer = pl.Trainer(accelerator="gpu", 
                         devices=1, 
                         max_epochs=config["epoch"], 
                         callbacks=[checkpoint_callback,early_stop_custom_callback],
                         log_every_n_steps=1,
                         logger=wandb_logger)
    
    ## resume ##
    if config['resume_path']:
        trainer.fit(model=model, datamodule=dataloader,ckpt_path=config['resume_path'])
    else:
        trainer.fit(model=model, datamodule=dataloader)


    ## best_model ##
    model = Model.load_from_checkpoint(checkpoint_callback.best_model_path, model_name=config["model_name"], lr=config["learning_rate"], tokenizer=dataloader.tokenizer)

    os.makedirs('./best_model', exist_ok=True)
    torch.save(model.model.state_dict(), f'./best_model/{config["model_detail"]}.pt')


if __name__ == '__main__':
    main()