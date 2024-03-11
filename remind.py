from transformers import AutoTokenizer, BartForConditionalGeneration
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
import argparse
from huggingface_hub import snapshot_download
import os

def download_backbone_model(MODEL_PATH):
    model_file = MODEL_PATH+"OPEN-SOLAR-KO-10_7B.Q5_K_S.gguf"
    if not os.path.isfile(model_file):
        snapshot_download(repo_id="ywhwang/OPEN-SOLAR-KO-10.7B", local_dir=MODEL_PATH,
                        local_dir_use_symlinks=False, revision="main")

def read_dialogue():
    user_dialogue = []
    f = open("luna_ver1.txt", 'r')
    cnt = 0
    while True:
        cnt += 1
        line = f.readline()
        if not line: break
        if cnt % 6 == 2: 
            user_dialogue.append(line.replace('\n',''))
    f.close()
    return user_dialogue

def summarize(dialogue=read_dialogue()):
    model_name = "alaggung/bart-r3f"
    max_length = 64
    num_beams = 5
    length_penalty = 1.2
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)
    model.eval()

    dialogue_summary = ""
    chunk_len = len(dialogue) // 5
    for i in range(chunk_len):
        dialogue_input = "[BOS]" + "[SEP]".join(dialogue[5*i:5*(i+1)]) + "[EOS]"
        inputs = tokenizer(dialogue_input, return_tensors="pt")
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            num_beams=num_beams,
            length_penalty=length_penalty,
            max_length=max_length,
            use_cache=True,
        )
        summarization = tokenizer.decode(outputs[0], skip_special_tokens=True)
        dialogue_summary = dialogue_summary + " " + summarization
    return dialogue_summary
    
def make_remind(template, dialogue_summary, user_name):
    n_gpu_layers = -1  # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
    n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    MODEL_PATH = "./"
    # Make sure the model path is correct for your system!
    solar = LlamaCpp(
        model_path= MODEL_PATH + "/OPEN-SOLAR-KO-10_7B.Q5_K_S.gguf",
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager,
        temperature=0.6,
        top_p=1,
        max_tokens=128,
        # stop=["Person1:", "Person2:"],
        verbose=True,  # Verbose is required to pass to the callback manager
    )
    prompt = PromptTemplate.from_template(template)
    solar_chain = LLMChain(prompt=prompt, llm=solar)
    remind = solar_chain.run({'context_list' : dialogue_summary, 'user_name':user_name})
    return remind

if __name__ == "__main__":
    MODEL_PATH = "./"
    download_backbone_model(MODEL_PATH=MODEL_PATH)
    dialogue_summary = summarize()
    print("summary\n", dialogue_summary)
    template = '''보고서는 {user_name}의 하루를 기록한 내용이야. 다음 지침과 예시를 참고해서 회고를 작성해줘.
                [System command]
                1. {user_name}의 하루를 루나라는 친구가 평가하는 내용을 작성해줘.
                2. 친구가 {user_name}에게 말해주는 것처럼 친근한 말투로 써줘.
                3. 모든 문장을 과거형으로 작성해줘.

                [Example Prompt]
                보고서: 고등학교 친구인 예원이를 만나서 카페를 다녀왔다고 한다.
                집에 돌아와서 피곤했지만 집 청소까지 마무리하고 침대에 누웠다고 한다.
                많은 것들을 하고 하루가 알차서 뿌듯한 기분이었다고 한다.
                회고: {user_name}아! 너는 오늘 고등학교 친구 예원이랑 만나서 카페를 다녀왔었네.
                {user_name}는 피곤했는데 집 청소까지 마무리하고 정말 대단해. 친구로서 너를 아주 칭찬해!
                오늘은 {user_name}에게 뿌듯하고 알찬 하루가 된 것 같아서 아주 대단하다고 생각해! 내일도 화이팅!

                보고서: {context_list}
                회고:'''
    remind = make_remind(template=template, dialogue_summary=dialogue_summary, user_name="수정")
    print("remind\n",remind)