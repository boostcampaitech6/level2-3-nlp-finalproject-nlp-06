from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.chains import LLMChain

from loguru import logger
import numpy as np
from typing import Optional, List, Tuple

from database import Retrospective, get_db_session
from model import get_tf_model, get_llm_chains, make_summary, async_func
from schemas import (
    ModelGenerationRequest,
    ModelGenerationResponse,
    RetrospectiveRequest, 
    RetrospectiveResponse
)


router = APIRouter()



@router.post("/generate/tf")
async def generate_tf_model(request: ModelGenerationRequest,
                            tf_model: tuple = Depends(get_tf_model)) -> ModelGenerationResponse:
    device, tokenizer, model = tf_model
    inputs = tokenizer(request.text, return_tensors="pt", padding=True, truncation=True).to(device)
    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask, 
        max_length=64, num_beams=5, length_penalty=1.2, use_cache=True, early_stopping=True
    ).detach().cpu()
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return ModelGenerationResponse(text=text)



@router.post("/generate/chains")
async def generate_chain(request: ModelGenerationRequest,
                         llm_chains: Tuple[LLMChain, LLMChain] = Depends(get_llm_chains)) -> ModelGenerationResponse:
    llm_retrospective_chain, llm_comment_chain = llm_chains
    
    retrospective_context = {
        "name": request.name,
        "summary": request.text
    }
    
    retrospective_result = await llm_retrospective_chain.ainvoke(input=retrospective_context)

    comment_context = {
        "name": request.name,
        "retrospective": retrospective_result.get("text")
    }

    comment_result = await llm_comment_chain.ainvoke(input=comment_context)

    result = retrospective_result.get("text") + "\n지우의 한마디 : " + comment_result.get("text")

    return ModelGenerationResponse(text=result)



@router.get("/predict/{username}")
async def get_predict_by_username(username: str, 
                                  db: AsyncSession = Depends(get_db_session)) -> List[RetrospectiveResponse]:
    result = await db.execute(select(Retrospective)
                              .filter(Retrospective.username == username))
    retrospectives = result.scalars().all()
    return [
        RetrospectiveResponse(
            id=retrospective.id,
            text=retrospective.text, 
            comment=retrospective.comment,
            date=retrospective.created_at
        ) for retrospective in retrospectives
    ]



@router.post("/predict")
async def predict(request: RetrospectiveRequest,
                  tf_model: tuple = Depends(get_tf_model),
                  llm_chains: Tuple[LLMChain, LLMChain] = Depends(get_llm_chains),
                  db: AsyncSession = Depends(get_db_session)) -> RetrospectiveResponse:
    device, tokenizer, model = tf_model
    llm_retrospective_chain, llm_comment_chain = llm_chains

    user_inputs = request.user_inputs
    user_inputs_length = len(user_inputs)

    chunks = []
    turns_per_chunk = 5
    total_chunks = user_inputs_length // turns_per_chunk if user_inputs_length % turns_per_chunk == 0 else user_inputs_length // turns_per_chunk + 1
    for i in range(total_chunks):
        start = i * turns_per_chunk
        end = (i + 1) * turns_per_chunk if (i + 1) * turns_per_chunk < user_inputs_length else user_inputs_length
        chunks.append("[BOS]" + "[SEP]".join(user_inputs[start:end]) + "[EOS]")
    
    summary = await async_func(make_summary, chunks, device, tokenizer, model)

    # logger.info(f"Summary: {summary}")

    retrospective_context = {
        "name": request.name,
        "summary": summary
    }
    
    retrospective_result = await llm_retrospective_chain.ainvoke(input=retrospective_context)
    retrospective_result = retrospective_result.get("text").strip()

    # logger.info(f"Retrospective: {retrospective_result}")

    comment_context = {
        "name": request.name,
        "retrospective": retrospective_result
    }

    comment_result = await llm_comment_chain.ainvoke(input=comment_context)
    comment_result = comment_result.get("text").strip()

    # logger.info(f"Comment: {comment_result}")

    # result = retrospective_result.get("text").strip() + "\n지우의 한마디 : " + comment_result.get("text").strip()

    retrospective = Retrospective(
        username=request.username,
        text=retrospective_result,
        comment=comment_result
    )

    db.add(retrospective)
    await db.commit()
    await db.refresh(retrospective)

    return RetrospectiveResponse(
        id=retrospective.id, 
        text=retrospective_result, 
        comment=comment_result, 
        date=retrospective.created_at
    )



@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             tf_model: tuple = Depends(get_tf_model),
                             llm_chains: Tuple[LLMChain, LLMChain] = Depends(get_llm_chains),
                             db: AsyncSession = Depends(get_db_session)):
    device, tokenizer, model = tf_model
    llm_retrospective_chain, llm_comment_chain = llm_chains
    
    await websocket.accept()
    await websocket.send_json({"message": "Connection successful"})

    try:
        while True:
            data = await websocket.receive_json()

            # from get("/predict")
            if data.get("type") == "get_predict":
                result = await db.execute(select(Retrospective)
                              .filter(Retrospective.username == data.get("username"))
                )
                retrospectives = result.scalars().all()
                
                response = {
                    "message": "success",
                    "body": [
                        {
                            "id": str(retrospective.id), #  if reference result from retrospective.id, must str(retrospective.id
                            "text": retrospective.text, 
                            "comment": retrospective.comment,
                            "date": retrospective.created_at.isoformat()
                        } for retrospective in retrospectives
                    ]
                }
                
                await websocket.send_json(response)
            
            # from post("/predict")
            elif data.get("type") == "post_predict":
                user_inputs = data.get("user_inputs")
                user_inputs_length = len(user_inputs)

                # logger.info(f"User inputs: {user_inputs}")

                chunks = []
                turns_per_chunk = 5
                total_chunks = user_inputs_length // turns_per_chunk if user_inputs_length % turns_per_chunk == 0 else user_inputs_length // turns_per_chunk + 1
                for i in range(total_chunks):
                    start = i * turns_per_chunk
                    end = (i + 1) * turns_per_chunk if (i + 1) * turns_per_chunk < user_inputs_length else user_inputs_length
                    chunks.append("[BOS]" + "[SEP]".join(user_inputs[start:end]) + "[EOS]")
                
                summary = await async_func(make_summary, chunks, device, tokenizer, model)

                # logger.info(f"Summary: {summary}")
                
                retrospective_context = {
                    "name": data.get("name"),
                    "summary": summary
                }
                
                retrospective_result = await llm_retrospective_chain.ainvoke(input=retrospective_context)
                retrospective_result = retrospective_result.get("text").strip()

                # logger.info(f"Retrospective: {retrospective_result}")

                comment_context = {
                    "name": data.get("name"),
                    "retrospective": retrospective_result
                }

                comment_result = await llm_comment_chain.ainvoke(input=comment_context)
                comment_result = comment_result.get("text").strip()

                # logger.info(f"Comment: {comment_result}")

                # result = retrospective_result.get("text").strip() + "\지우의 한마디 : " + comment_result.get("text").strip()

                retrospective = Retrospective(
                    username=data.get("username"),
                    text=retrospective_result,
                    comment=comment_result
                )

                db.add(retrospective)
                await db.commit()
                await db.refresh(retrospective)

                response = {
                    "message": "success",
                    "body": {
                        "id": str(retrospective.id),
                        # "text": result #  if reference result from retrospective.text, must await db.refresh(retrospective)
                    }
                } 
                await websocket.send_json(response)
            
            else:
                await websocket.send_json({"message": "error", "body": "Invalid request type."})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

    
    



