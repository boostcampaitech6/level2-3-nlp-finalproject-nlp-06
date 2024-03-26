from fastapi import APIRouter, HTTPException, Depends, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, delete
from langchain_core.embeddings import Embeddings

from loguru import logger
from typing import List
import json


from schemas import PredictRequest, UserPersonaRequest, UserPersonaResponse
from model import get_tf_model, get_embeddings, make_prediction, make_embeds, make_embed
from database import UserPersona, engine, get_db_session


router = APIRouter()


@router.post("/predict")
async def predict(request: PredictRequest, 
                  tokenizer_and_model: tuple = Depends(get_tf_model), 
                  embeddings: Embeddings = Depends(get_embeddings),
                  db: AsyncSession = Depends(get_db_session)) -> Response:
    device, tokenizer, model = tokenizer_and_model

    # logger.info(f"device: {device}")
    # logger.info(f"tokenizer: {tokenizer}")
    # logger.info(f"model: {model}")

    predictions = make_prediction(request.user_inputs, device, tokenizer, model)
    predictions = [prediction.strip() for prediction in predictions.replace(".", "").split(",") if prediction]

    embeds = make_embeds(predictions, embeddings)

    user_personas = [
        UserPersona(username=request.username, text=prediction, embedding=embed)
        for prediction, embed in zip(predictions, embeds)
    ]

    db.add_all(user_personas)
    await db.commit() # not refresh so that the id will be lately updated

    return JSONResponse(content={"message": "success"}, status_code=201)


@router.post("/persona")
async def get_persona(request: UserPersonaRequest, 
                      embeddings: Embeddings = Depends(get_embeddings),
                      db: AsyncSession = Depends(get_db_session)) -> List[UserPersonaResponse]:
    user_input_embed = make_embed(request.user_input, embeddings) 

    # https://github.com/pgvector/pgvector-python/blob/master/README.md#sqlmodel
    # l2_distance, cosine_distance, max_inner_product
    result = await db.execute(
        select(UserPersona)
        .filter(UserPersona.username == request.username)
        .order_by(UserPersona.embedding.cosine_distance(user_input_embed))
        .limit(request.top_k)
    )
    user_personas = result.scalars().all()

    if not user_personas:
        return JSONResponse(
            content={"message": "error", "body": f"No persona found for user {request.username}"}, 
            status_code=404
        )
    return [
        UserPersonaResponse(
            text=user_persona.text,
        )
        for user_persona in user_personas
    ]



@router.get("/persona/{username}")
async def get_persona_by_username(username: str, 
                                  db: AsyncSession = Depends(get_db_session)) -> List[UserPersonaResponse]:
    result = await db.execute(
        select(UserPersona)
        .filter(UserPersona.username == username)
    )
    user_personas = result.scalars().all()

    if not user_personas:
        return JSONResponse(
            content={"message": "error", "body": f"No persona found for user {username}"}, 
            status_code=404
        )
    return [
        UserPersonaResponse(
            text=user_persona.text,
        )
        for user_persona in user_personas
    ]



# maintain single connection from generation app
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             tokenizer_and_model: tuple = Depends(get_tf_model), 
                             embeddings: Embeddings = Depends(get_embeddings),
                             db: AsyncSession = Depends(get_db_session)):
    device, tokenizer, model = tokenizer_and_model
    embeddings = embeddings

    await websocket.accept()
    await websocket.send_json({"message":"Connection successful"})

    try:
        while True:
            data = await websocket.receive_json() # automatically parse json

            # from post("/predict")
            if data.get("type") == "post_predict":
                # Prepare some summary to send back
                predictions = make_prediction(data.get("user_inputs"), device, tokenizer, model)
                predictions = list(set([prediction.strip() for prediction in predictions.replace(".", "").split(",") if prediction])) # change to , based on the model output

                embeds = make_embeds(predictions, embeddings)

                user_personas = []
                for prediction, embed in zip(predictions, embeds):
                    await db.execute(
                        delete(UserPersona)
                        .filter(UserPersona.username == data.get("username"))
                        .filter(UserPersona.embedding.cosine_distance(embed) < 0.1)
                    )

                    user_personas.append(
                        UserPersona(username=data.get("username"), text=prediction, embedding=embed)
                    )

                # user_personas = [
                #     UserPersona(username=data.get("username"), text=prediction, embedding=embed)
                #     for prediction, embed in zip(predictions, embeds)
                # ]

                db.add_all(user_personas)
                await db.commit() # not refresh so that the id will be lately updated

                response = {
                    "message": "success"
                }
                await websocket.send_json(response)

            # from get("/persona")
            elif data.get("type") == "get_persona":
                user_input_embed = make_embed(data.get("user_input"), embeddings) 
                result = await db.execute(
                    select(UserPersona)
                    .filter(UserPersona.username == data.get("username"))
                    .filter(UserPersona.embedding.cosine_distance(user_input_embed) < 0.15) # .order_by(UserPersona.embedding.cosine_distance(user_input_embed))
                    .limit(data.get("top_k"))
                )
                user_personas = result.scalars().all()
                response = {
                    "message": "success",
                    "body": [{"text": user_persona.text} for user_persona in user_personas]
                }
                await websocket.send_json(response)

            else:
                await websocket.send_json({"message": "error", "body": "Invalid request type."})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")




