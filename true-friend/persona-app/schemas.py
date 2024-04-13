from pydantic import BaseModel, Field

from typing import List

class PredictRequest(BaseModel):
    username: str
    user_inputs: List[str]


class UserPersonaRequest(BaseModel):
    username: str
    user_input: str
    top_k: int = 5 # set default value to 5


class UserPersonaResponse(BaseModel):
    text: str
    # similarity_score: float