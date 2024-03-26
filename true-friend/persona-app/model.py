from dotenv import load_dotenv
from typing import List
from tqdm.auto import tqdm

from transformers import (
    AutoConfig, 
    AutoTokenizer, 
    AutoModelForCausalLM, 
    T5ForConditionalGeneration, 
    T5Model
)
from langchain_openai import OpenAIEmbeddings
import torch

from config import config

tf_device, tf_tokenizer, tf_model = None, None, None
embeddings = None
 

def load_tf_model():
    global tf_device
    tf_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    global tf_tokenizer
    tf_tokenizer = AutoTokenizer.from_pretrained(config.tf_model_id, token=config.hf_token)

    global tf_model
    tf_model = T5ForConditionalGeneration.from_pretrained(config.tf_model_id, token=config.hf_token).to(tf_device)


def get_tf_model():
    return tf_device, tf_tokenizer, tf_model


def load_embeddings():
    # https://api.python.langchain.com/en/latest/embeddings/langchain_openai.embeddings.base.OpenAIEmbeddings.html
    global embeddings
    embeddings = OpenAIEmbeddings()


def get_embeddings():
    return embeddings


def make_prediction(text: List[str], device: torch.device, tokenizer: AutoTokenizer, model: T5Model) -> str:
    concat_text = '[BOS] ' + ' [SEP] '.join(text) + ' </s>'
    inputs = tokenizer(concat_text, padding='max_length', max_length=200 ,return_tensors="pt", truncation=True).to(device)
    
    outputs = model.generate(inputs["input_ids"],  max_length=200, num_beams=2, early_stopping=True).detach().cpu().numpy()
    summary = tokenizer.decode(outputs.squeeze(), skip_special_tokens=True)
    return summary


def make_embed(text: str, embeddings: OpenAIEmbeddings) -> List[float]:
    return embeddings.embed_query(text)


def make_embeds(text: List[str], embeddings: OpenAIEmbeddings) -> List[List[float]]:
    return embeddings.embed_documents(text)


if __name__ == "__main__":
    

    print(make_prediction(['a', 'b', 'c']))

    concat_text = """
    [BOS] 안녕하세요! 저는 인천 사는 10대 남자입니다 
    [SEP] 네 만나서 반가워요 요즘 학교에서 동아리 활동을 하고 있는데 즐겁네요 ᄒᄒ 
    [SEP] 법무사라니 멋진 직업이네요 ᄒᄒ 아직 대학 가기전이라서 놀고 있습니다 ᄏᄏ 
    [SEP] 해외여행 자주 다니셨나 봐요? 저는 부모님 따라서 국내여행만 다녔어요 ᄒᄒ 
    [SEP] 네 부모님이랑 여행 가는 걸 좋아해요 ᄒᄒ 가서도 모르는 사람이랑 잘 어울리거든요. 
    [SEP] 다른 취미는 게임이나 음악 듣는걸 좋아합니다 ᄒᄒ 내성적이시면 활동적인 취미를 안좋아하시나봐요? 
    [SEP] 저는 양식이랑 한식 좋아하고 중식은 속이 더부룩해서 싫더라고요. 법무사님은 좋아하시는 음식이 있으신가요? [EOS]
    """