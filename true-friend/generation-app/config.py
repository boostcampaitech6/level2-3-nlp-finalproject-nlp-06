from pydantic import Field
from pydantic_settings import BaseSettings

import os

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_URL = f"redis://{REDIS_HOST}"
LLM_MODEL_PATH = os.environ.get("LLM_MODEL_PATH")
PERSONA_APP_NAME = os.environ.get("PERSONA_APP_NAME")
PERSONA_APP_PORT = os.environ.get("PERSONA_APP_PORT")
PERSONA_APP_WS_URL = f"ws://{PERSONA_APP_NAME}:{PERSONA_APP_PORT}/ws"
RETROSPECTIVE_APP_NAME = os.environ.get("RETROSPECTIVE_APP_NAME")
RETROSPECTIVE_APP_PORT = os.environ.get("RETROSPECTIVE_APP_PORT")
RETROSPECTIVE_APP_WS_URL = f"ws://{RETROSPECTIVE_APP_NAME}:{RETROSPECTIVE_APP_PORT}/ws"
RETROSPECTIVE_SCHEDULER_HOUR = os.environ.get("RETROSPECTIVE_SCHEDULER_HOUR")
RETROSPECTIVE_SCHEDULER_MINUTE = os.environ.get("RETROSPECTIVE_SCHEDULER_MINUTE")


class Config(BaseSettings):
    redis_url: str = Field(default=REDIS_URL, env="REDIS_URL")
    llm_model_path: str = Field(default=LLM_MODEL_PATH, env="MODEL_PATH")
    persona_app_ws_url: str = Field(default=PERSONA_APP_WS_URL, env="PERSONA_APP_WS_URL")
    retrospective_app_ws_url: str = Field(default=RETROSPECTIVE_APP_WS_URL, env="RETROSPECTIVE_APP_WS_URL")
    retrospective_scheduler_hour: int = Field(default=RETROSPECTIVE_SCHEDULER_HOUR, env="RETROSPECTIVE_SCHEDULER_HOUR")
    retrospective_scheduler_minute: int = Field(default=RETROSPECTIVE_SCHEDULER_MINUTE, env="RETROSPECTIVE_SCHEDULER_MINUTE")

config = Config()