from pydantic import BaseModel, Field
from typing import List
import datetime



class ModelGenerationRequest(BaseModel):
    username: str
    name: str
    text: str


class ModelGenerationResponse(BaseModel):
    text: str


class RetrospectiveRequest(BaseModel):
    username: str
    name: str
    user_inputs: List[str]
    bot_responses: List[str]


class RetrospectiveResponse(BaseModel):
    text: str
    comment: str
    date: datetime.datetime

