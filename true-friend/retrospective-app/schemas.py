from pydantic import BaseModel, Field
from typing import List
import datetime
import uuid



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
    id: uuid.UUID
    text: str
    comment: str
    date: datetime.datetime

