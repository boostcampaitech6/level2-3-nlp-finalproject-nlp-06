from transformers import AutoConfig, AutoTokenizer, PreTrainedModel, BartForConditionalGeneration
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks import StdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain.chains import LLMChain

import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List
from loguru import logger

from config import config


tf_device, tf_tokenizer, tf_model = None, None, None
llm_retrospective_chain, llm_comment_chain = None, None


def load_tf_model():
    tf_config = AutoConfig.from_pretrained(config.tf_model_id)

    global tf_device
    tf_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    global tf_tokenizer
    tf_tokenizer = AutoTokenizer.from_pretrained(config.tf_model_id)
    
    global tf_model
    tf_model = BartForConditionalGeneration.from_pretrained(config.tf_model_id, config=tf_config).to(tf_device)


def get_tf_model():
    return tf_device, tf_tokenizer, tf_model


def make_summary(chunks: List[str], device: torch.device, tokenizer: AutoTokenizer, model: PreTrainedModel) -> str:
    inputs = tokenizer(chunks, return_tensors="pt", padding=True, truncation=True, max_length=64).to(device)
    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask, 
        max_length=64, num_beams=5, length_penalty=1.2, use_cache=True, early_stopping=True).detach().cpu()
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return "".join(summary)


def async_func(sync_func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return loop.run_in_executor(pool, sync_func, *args, **kwargs) # sync_func(*args, **kwargs)



def load_llm_chains():
    # https://huggingface.co/hyeogi/SOLAR-10.7B-v1.2/discussions/1
    # template = """### System:\n{input}\n\n### User:\n{instruction}\n### Assistant:\n"""

    callback_manager = CallbackManager([StdOutCallbackHandler()])
    model_path = config.llm_model_path
    stop_words = ['보고서:', '회고:', '#', '[System command]', '[Example Prompt]', '\n\n']

    try:
        # https://github.com/abetlen/llama-cpp-python
        llm = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=-1,
            n_batch=512,
            callback_manager=callback_manager,
            temperature=0.8,
            top_p=1,
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
            verbose=True,
        )
        logger.info(f"Loaded model from {model_path}")
    except Exception as e:
        logger.error(f"Error while loading model from {model_path}: {e}")
        llm = None


    retrospective_template = '''보고서는 {name}의 하루를 기록한 내용이야. 다음 지침과 예시를 참고해서 회고를 작성해줘.
    [System Command]
    1. {name}의 하루를 루나라는 친구가 평가하는 내용을 작성해줘.
    2. 친구가 {name}에게 말해주는 것처럼 친근한 말투로 써줘.
    3. 모든 문장을 과거형으로 작성해줘.

    [Example Prompt]
    보고서: 고등학교 친구인 예원이를 만나서 카페를 다녀왔다고 한다.
    집에 돌아와서는 너무 늦게 들어왔다는 이유로 엄마와 다퉜다고 한다.
    기분이 좋지 않았는데 대학 과제를 해야했기 때문에 열심히 다 마치고 잤다고 한다.
    회고: {name}아! 너는 오늘 고등학교 친구 예원이랑 만나서 카페를 다녀왔었네. 재미있었어? {name}는 집에 늦게 들어왔다고 엄마와 다퉜었지. 속상했겠다.. 그리고 기분이 좋지 않았는데도 대학 과제를 마무리하고 잤구나. {name}는 대단한 것 같아!

    보고서: {summary}
    회고:'''

    comment_template = '''주어진 회고는 루나라는 친구가 {name}의 하루를 기록한 내용이야. 다음 예시처럼 루나의 한마디를 작성해줘.
    [System Command]
    1. {name}의 하루가 감정적으로 즐거웠는지, 슬펐는지, 어땠는지 언급해줘.
    2. 항상 응원하는 친구가 {name}에게 응원하거나, 조언해주는 문장을 작성해줘.

    [Example Prompt]
    회고: {name}아! 너는 오늘 고등학교 친구 예원이랑 만나서 카페를 다녀왔었네. 재미있었어? {name}는 집에 늦게 들어왔다고 엄마와 다퉜었지. 속상했겠다.. 그리고 기분이 좋지 않았는데도 대학 과제를 마무리하고 잤구나. {name}는 대단한 것 같아!
    루나의 한마디: 오늘은 기분이 좋은 일도, 나쁜 일도 있었네. {name}가 항상 행복했으면 좋겠다!

    회고: {retrospective}
    루나의 한마디:'''

    retrospective_prompt = PromptTemplate.from_template(retrospective_template)
    comment_prompt = PromptTemplate.from_template(comment_template)

    global llm_retrospective_chain
    llm_retrospective_chain = LLMChain(prompt=retrospective_prompt, llm=llm)

    global llm_comment_chain
    llm_comment_chain = LLMChain(prompt=comment_prompt, llm=llm)


def get_llm_chains() -> tuple[LLMChain, LLMChain]:
    return llm_retrospective_chain, llm_comment_chain


