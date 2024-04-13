from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings

import os



DB_USERNAME = os.environ.get("DB_USERNAME") 
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
TF_MODEL_ID = os.environ.get("TF_MODEL_ID")
HF_TOKEN = os.environ.get("HF_TOKEN")
EMBEDDING_MODEL_ID = os.environ.get("EMBEDDING_MODEL_ID")

class Config(BaseSettings):
    db_url: str = Field(default=DB_URL, env="DB_URL")
    tf_model_id: str = Field(default=TF_MODEL_ID, env="TF_MODEL_ID")
    hf_token: str = Field(default=HF_TOKEN, env="HF_TOKEN")
    embedding_model_id: str = Field(default=EMBEDDING_MODEL_ID, env="EMBEDDING_MODEL_ID")


config = Config()
    