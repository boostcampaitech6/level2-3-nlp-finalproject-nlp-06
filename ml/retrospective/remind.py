from transformers import AutoTokenizer, BartForConditionalGeneration
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
import argparse
from huggingface_hub import snapshot_download
import os
import math

def download_backbone_model(MODEL_PATH):
    model_file = MODEL_PATH+"OPEN-SOLAR-KO-10_7B.Q5_K_S.gguf"
    if not os.path.isfile(model_file):
        snapshot_download(repo_id="ywhwang/OPEN-SOLAR-KO-10.7B", local_dir=MODEL_PATH,
                        local_dir_use_symlinks=False, revision="main")

def read_dialog(file_path):
    user_dialog = []
    f = open(file_path, 'r')
    cnt = 0
    while True:
        cnt += 1
        line = f.readline()
        if not line: break
        if cnt % 6 == 2: 
            user_dialog.append(line.replace('\n',''))
    f.close()
    return user_dialog

def summarize(dialog, chunk_size):
    model_name = "alaggung/bart-r3f"
    max_length = 128
    num_beams = 5
    length_penalty = 1.2
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    model.eval()

    dialog_summary = ""
    for i in range(0, len(dialog), chunk_size):
        chunk = "".join(dialog[i:i + chunk_size])
        dialog_input = "[BOS]" + "[SEP]" + chunk + "[EOS]"
        inputs = tokenizer(dialog_input, return_tensors="pt")
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            num_beams=num_beams,
            length_penalty=length_penalty,
            max_length=max_length,
            use_cache=True,
        )
        summarization = tokenizer.decode(outputs[0], skip_special_tokens=True)
        dialog_summary = dialog_summary + " " + summarization
    return dialog_summary[1:]
    
def make_remind(bot_summary_template, comment_template, dialog_summary, user_name, stop_words=None):
    n_gpu_layers = -1  # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
    n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    MODEL_PATH = "./"

    # make bot_summary
    solar = LlamaCpp(
        model_path= MODEL_PATH + "/OPEN-SOLAR-KO-10_7B.Q5_K_S.gguf",
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager,
        temperature=0.8,
        top_p=1,
        top_k=30,
        max_tokens=256,
        c=2048,
        model_kwargs={
        'min_p':0.7,
        'repeatition_penalty': 1.9,
        'no_repeat_ngram_size': 6,
        'repeat_last_n' : 10,
        'early_stopping': True
        },
        stop=stop_words,
        verbose=True,  # Verbose is required to pass to the callback manager
    )
    prompt = PromptTemplate.from_template(bot_summary_template)
    solar_chain = LLMChain(prompt=prompt, llm=solar)
    bot_summary = solar_chain.run({'context_list' : dialog_summary, 'user_name':user_name})

    # make last comment
    prompt = PromptTemplate.from_template(comment_template)
    solar_chain = LLMChain(prompt=prompt, llm=solar)
    last_comment = solar_chain.run({'context_list' : bot_summary, 'user_name':user_name})

    remind = bot_summary + '\n 지우의 한마디 : ' + last_comment
    return remind


if __name__ == "__main__":
    MODEL_PATH = "./"
    user_name = '수정'
    download_backbone_model(MODEL_PATH=MODEL_PATH)
    stop_words = ['보고서:', '회고:', '#', '[System command]', '[Example Prompt]', '\n\n']
    dialog = read_dialog("./dialog/dialog_solar_jiu/dialog_history_short.txt")
    if len(dialog) <= 5:
        remind = f"지우는 {user_name}과 조금 더 이야기 하고 싶나봐요!"
    else:
        dialog_summary = summarize(dialog, chunk_size=4)
        bot_summary_template = '''보고서는 {user_name}의 하루를 기록한 내용이야. 다음 지침과 예시를 참고해서 회고를 작성해줘.
    [System command]
    1. {user_name}의 하루를 지우라는 친구가 평가하는 내용을 작성해줘.
    2. 친구가 {user_name}에게 말해주는 것처럼 친근한 말투로 써줘.
    3. 모든 문장을 과거형으로 작성해줘.

    [Example Prompt]
    보고서: 고등학교 친구인 예원이를 만나서 카페를 다녀왔다고 한다.
    집에 돌아와서는 너무 늦게 들어왔다는 이유로 엄마와 다퉜다고 한다.
    기분이 좋지 않았는데 대학 과제를 해야했기 때문에 열심히 다 마치고 잤다고 한다.
    회고: {user_name}아! 너는 오늘 고등학교 친구 예원이랑 만나서 카페를 다녀왔었네. 재미있었어? {user_name}는 집에 늦게 들어왔다고 엄마와 다퉜었지. 속상했겠다.. 그리고 기분이 좋지 않았는데도 대학 과제를 마무리하고 잤구나. {user_name}는 대단한 것 같아!

    보고서: {context_list}
    회고:'''
        
        comment_template = '''주어진 회고는 지우라는 친구가 {user_name}의 하루를 기록한 내용이야. 다음 예시처럼 지우의 한마디를 작성해줘.
    [System command]
    1. {user_name}의 하루가 감정적으로 즐거웠는지, 슬펐는지, 어땠는지 언급해줘.
    2. 항상 응원하는 친구가 {user_name}에게 응원하거나, 조언해주는 문장을 작성해줘.

    [Example Prompt]
    회고: {user_name}아! 너는 오늘 고등학교 친구 예원이랑 만나서 카페를 다녀왔었네. 재미있었어? {user_name}는 집에 늦게 들어왔다고 엄마와 다퉜었지. 속상했겠다.. 그리고 기분이 좋지 않았는데도 대학 과제를 마무리하고 잤구나. {user_name}는 대단한 것 같아!
    지우의 한마디: 오늘은 기분이 좋은 일도, 나쁜 일도 있었네. {user_name}가 항상 행복했으면 좋겠다!

    회고:{context_list}
    지우의 한마디:'''

        remind = make_remind(bot_summary_template, comment_template, dialog_summary, user_name=user_name, stop_words=stop_words)
        print("summary\n", dialog_summary)
    print("remind\n",remind)