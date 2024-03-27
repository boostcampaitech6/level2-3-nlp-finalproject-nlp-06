from pydantic import BaseModel
from typing import List
import datetime
import uuid


class GenerationRequest(BaseModel):
    username: str
    name: str
    text: str


class GenerationResponse(BaseModel):
    text: str
    personas: List[str]


class SessionIdResponse(BaseModel):
    id: str


class TurnResponse(BaseModel):
    user_input: str
    bot_response: str


class PersonaRequest(BaseModel):
    username: str


class RetrospectiveRequest(BaseModel):
    username: str
    name: str
    remove_history: bool = False


class RetrospectiveResponse(BaseModel):
    id: uuid.UUID
    text: str
    comment: str
    date: datetime.datetime


    

