from pydantic import Field
from pydantic_settings import BaseSettings

import os



DB_USERNAME = os.environ.get("DB_USERNAME") 
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
TF_MODEL_ID = os.environ.get("TF_MODEL_ID")
LLM_MODEL_PATH = os.environ.get("LLM_MODEL_PATH")


class Config(BaseSettings):
    db_url: str = Field(default=DB_URL, env="DB_URL")
    tf_model_id: str = Field(default=TF_MODEL_ID, env="TF_MODEL_ID") # transformers
    llm_model_path: str = Field(default=LLM_MODEL_PATH, env="LLM_MODEL_PATH") # langchain llamacpp gguf


config = Config()
