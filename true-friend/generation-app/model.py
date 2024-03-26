from langchain.callbacks.manager import CallbackManager
from langchain.callbacks import StdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_community.llms import LlamaCpp
from langchain.chains import LLMChain

from config import config

from loguru import logger
from typing import Optional
import os


llm_chain = None

def load_llm_chain():
    template="""지금부터 아래의 [챗봇 정보]를 가진 인물이 되어 대화를 수행한다.
    [챗봇 정보]
    - 이름: 지우
    - 나이: 25세
    - 직업: 대학생, 커뮤니케이션학과 전공

    [사용자 기본 정보]
    - 이름: {user_name}
    - 나이: {user_age}
    - 성별: {user_sex}

    [대화 예시]
    {user_name}: 넌 이름이 뭐야?
    지우: 나는 지우야! 너는 {user_name}이지?\n

    [현재 발화 관련 정보]
    {user_persona}

    지금까지의 프롬프트를 읽고 [챗봇 정보]의 인물이 되어 대답하고, [사용자 정보]와 [현재 발화 관련 정보]에 기반하여 친절하고 예의있게 답변하라.
    {history}
    {user_name}: {input}
    지우: """

    prompt = PromptTemplate.from_template(template)

    # callback_manager = CallbackManager([StdOutCallbackHandler()])
    # model_path = config.llm_model_path
    # # stop_words = ["예원:", "지우:", "\n", "ᄏ"*6, "ᄒ"*6, "ㅠ"*6, "ᄋ"*6, "ㅋ"*6, "ㅎ"*6, "ㅠ"*6, "ㅇ"*6]

    # try:
    #     # https://api.python.langchain.com/en/latest/llms/langchain_community.llms.llamacpp.LlamaCpp.html
    #     llm = LlamaCpp(
    #         model_path=model_path,
    #         n_gpu_layers=30,
    #         n_batch=4096,
    #         callback_manager=callback_manager,
    #         temperature=0.9,
    #         top_p=0.95,
    #         top_k=30,
    #         max_tokens=256,
    #         n_ctx=2048,
    #         # stop=stop_words,
    #         model_kwargs={
    #             'min_p':0.7,
    #             'repeatition_penalty': 1.4,
    #             'no_repeat_ngram_size': 6,
    #             'repeat_last_n' : 10,
    #             'early_stopping': True
    #         },
    #         verbose=True,  # Verbose is required to pass to the callback manager
    #     )
    #     logger.info(f"Loaded model from {model_path}")
    # except Exception as e:
    #     logger.error(f"Error while loading model from {model_path}: {e}")
    #     llm = None
    
    llm = OpenAI(temperature=0.8,
                 max_tokens=150,
                 top_p=0.8,
                 frequency_penalty=0.5,
                 presence_penalty=0.5,
                 stop=['\n'])

    global llm_chain
    llm_chain = LLMChain(prompt=prompt, llm=llm)


def get_llm_chain():
    return llm_chain



# template = """
# [Chatbot Persona Prompt]
# 발랄하고 잘 웃는 긍정왕 고등학교 2학년 학생인 루나는 {user_name}의 오늘의 일상과 관심사에 대해 물어보고 듣는 것을 좋아해. {user_name}와 친근하게 반말로 대화해줘.

# [History Prompt]
# {user_name}의 현재 발화와 관련된 이전 발화 정보를 참조하여 친근하게 반말로 대화해줘.
# {history}

# [{user_name} Persona Prompt]
# {user_name}의 Persona는 루나가 이전에 대화를 통해 얻어낸 {user_name}의 Persona이다.
# 루나는 {user_name}의 Persona들을 이미 확실히 아는 듯이 언급하면서 대화해줘
# {user_name}의 Persona: 나는 {user_name}이다, {user_age}이다, {user_sex}이다, {user_persona}

# (지금까지의 프롬프트를 다시 한번 읽고 대답해줘)
# [Current Conversation]
# {user_name}: {input}
# 루나: """