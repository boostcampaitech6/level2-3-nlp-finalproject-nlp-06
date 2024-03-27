from fastapi import APIRouter, HTTPException, status, WebSocket, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from redis.asyncio import Redis
from langchain.chains import LLMChain
import httpx

from loguru import logger
import json
import uuid
from typing import List
from datetime import datetime

from schemas import (
    GenerationRequest, 
    GenerationResponse, 
    SessionIdResponse, 
    TurnResponse,
    PersonaRequest, 
    RetrospectiveRequest,
    RetrospectiveResponse
) 
from model import get_llm_chain
from database import get_redis
from websocket import WebSocketClient
from config import config




router = APIRouter()

# redis save format
# {
#     "chat_history:username": [
#         {
#             "user_input": "안녕? 넌 이름이 뭐니?",
#             "bot_response": "전 AI입니다. 이름은 없습니다.",
#         }
#     ]
# }

@router.post("/generate")
async def generate(request: GenerationRequest,
                   llm_chain: LLMChain = Depends(get_llm_chain),
                   redis: Redis = Depends(get_redis)) -> GenerationResponse:
    websocket_client = WebSocketClient(uri=config.persona_app_ws_url)
    await websocket_client.handshake()

    name_key = f"username:{request.username}"
    if not redis.exists(name_key):
        await redis.set(name_key, request.name)
    
    key = f"chat_history:{request.username}"
    user_input = request.text

    # get persona
    persona_data = {
        "type": "get_persona",
        "username": request.username,
        "user_input": user_input,
        "top_k": 3
    }

    await websocket_client.send(persona_data)
    response = await websocket_client.receive()

    if response.get("message") != "success":
        return JSONResponse({"message": "error", "body": "Failed to get persona"}, status_code=404)

    user_personas = [user_persona.get("text") for user_persona in response.get("body")]
    concat_personas = ", ".join(user_personas)

    # logger.info(f"User personas:\n{concat_personas}")

    # get history
    # should work if no key exists (initial user input)
    history = ""
    turns = await redis.lrange(key, 0, 2) 
    if len(turns) > 0:
        turns = [json.loads(turn.decode("utf-8")) for turn in turns[::-1]]
        for turn in turns:
            # history += f"{request.name}: " + turn.get("user_input") + "\n"
            # history += "지우: " + turn.get("bot_response") + "\n"
            # history 변경
            history += f'예원: {turn.get("user_input")}\n지우: {turn.get("bot_response")}\n'

    # else:
    #     history += f"{request.name}: \n"
    #     history += "지우: \n"
    #     history += f'{request.name}: \n지우: {turn.get("bot_response")}\n'
        
            

    print(f"History:\n{history}")
    # logger.info(f"History:\n{history}")

    context = {
        # "user_name": request.name,
        "user_name": "예원",
        "user_age": "25",
        "user_sex": "여자",
        "user_persona": concat_personas,
        "history": history,
        "input": user_input
    }

    print(context)

    bot_response = await llm_chain.ainvoke(context)
    print(f"\nBot response: {bot_response.get('text')}\n")

    redis_data = {
        "user_input": user_input,
        "bot_response": bot_response.get("text").strip()
    }
    await redis.lpush(key, json.dumps(redis_data))

    turn_count = await redis.llen(key)
    if turn_count % 10 == 0:
        turns = await redis.lrange(key, 0, 9)
        turns = [json.loads(turn.decode("utf-8")) for turn in turns[::-1]]
        predict_data = {
            "type": "post_predict",
            "username": request.username,
            "user_inputs": [turn.get("user_input") for turn in turns]
        }

        await websocket_client.send(predict_data)
        response = await websocket_client.receive()

        if response.get("message") != "success":
            return JSONResponse({"message": "error", "body": "Failed to create persona"}, status_code=422)

        # print(f"\nPersona prediction request response: {response}\n")

    await websocket_client.close()
    del websocket_client

    return GenerationResponse(
        text=bot_response.get('text').strip(),
        personas=user_personas
    )


# get usernames (a.k.a. session ids) currently saved in redis
@router.get("/sessions")
async def get_session_ids(redis: Redis = Depends(get_redis)) -> List[SessionIdResponse]:
    pattern = "chat_history:*"
    cursor = '0' # should be str 0
    matching_keys = []
    while cursor != 0: # should be int 0
        cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
        matching_keys.extend(keys)

    return [
        SessionIdResponse(id=key.decode("utf-8").split(":")[1]) for key in matching_keys
    ]



@router.get("/sessions/{session_id}")
async def get_session_turns(session_id: str, 
                            redis: Redis = Depends(get_redis)) -> List[TurnResponse]:
    key = f"chat_history:{session_id}"
    
    if not await redis.exists(key):
        return JSONResponse({"message": "error", "body": "No data found for this user"}, status_code=404)
    
    turns = await redis.lrange(key, 0, -1)
    turns = [json.loads(turn.decode("utf-8")) for turn in turns[::-1]]
    return [
        TurnResponse(
            user_input=turn.get("user_input"),
            bot_response=turn.get("bot_response")
        ) for turn in turns
    ]



@router.post("/persona")
async def predict_persona_by_user(request: PersonaRequest,
                                  redis: Redis = Depends(get_redis)):
    websocket_client = WebSocketClient(uri=config.persona_app_ws_url)
    await websocket_client.handshake()

    key = f"chat_history:{request.username}"

    if not await redis.exists(key):
        return JSONResponse({"message": "error", "body": "No data found for this user"}, status_code=404)

    turns = await redis.lrange(key, 0, -1)
    turns = [json.loads(turn.decode("utf-8")) for turn in turns[::-1]]
    data = {
        "type": "post_predict",
        "username": request.username,
        "user_inputs": [turn.get("user_input") for turn in turns],
    }

    # logger.info(f"Persona prediction request data: {data}")

    await websocket_client.send(data)
    response = await websocket_client.receive()

    # logger.info(f"Persona prediction request response: {response}")

    if response.get("message") != "success":
        return JSONResponse({"message": "error", "body": "Failed to predict persona"}, status_code=422)
    
    await websocket_client.close()
    del websocket_client

    return JSONResponse({"message": "success"}, status_code=200)



# test function
@router.post("/persona/test")
async def predict_persona():
    websocket_client = WebSocketClient(uri=config.persona_app_ws_url)
    await websocket_client.handshake()

    data = {
        "type": "post_predict",
        "username": "test",
        "user_inputs": [
            "안녕하세요! 저는 인천 사는 10대 남자입니다.",
            "아직 대학 가기전이라서 놀고 있습니다.",
            "네 만나서 반가워요 요즘 학교에서 동아리 활동을 하고 있는데 즐겁네요!",
            "다른 취미는 게임이나 음악 듣는걸 좋아합니다.",
            "저는 양식이랑 한식 좋아하고 중식은 속이 더부룩해서 싫더라고요."
        ]
    }

    await websocket_client.send(data)
    response = await websocket_client.receive()

    if response.get("message") != "success":
        return JSONResponse({"message": "error", "body": "Failed to predict persona"}, status_code=422)
    
    await websocket_client.close()
    del websocket_client

    return JSONResponse({"message": "success"}, status_code=200)



@router.get("/retrospective/{username}")
async def get_retrospective_by_user(username: str) -> List[RetrospectiveResponse]:
    websocket_client = WebSocketClient(uri=config.retrospective_app_ws_url)
    await websocket_client.handshake()

    data = {
        "type": "get_predict",
        "username": username
    }
    await websocket_client.send(data)
    response = await websocket_client.receive() # {"message": "success", "body": [{"text": "retrospective text", "date": "2021-08-01T00:00:00"}]} # date is in isoformat

    if response.get("message") != "success":
        return JSONResponse({"message": "error", "body": "Failed to get retrospective"}, status_code=422)
    
    await websocket_client.close()
    del websocket_client

    return [
        RetrospectiveResponse(
            id=uuid.UUID(retrospective.get("id")),
            text=retrospective.get("text"), 
            comment=retrospective.get("comment"), 
            date=datetime.fromisoformat(retrospective.get("date"))
        ) for retrospective in response.get("body")
    ]



@router.post("/retrospective")
async def predict_retrospective_by_user(request: RetrospectiveRequest, 
                                        redis: Redis = Depends(get_redis)):
    websocket_client = WebSocketClient(uri=config.retrospective_app_ws_url)
    await websocket_client.handshake()

    key = f"chat_history:{request.username}"

    if not await redis.exists(key):
        return JSONResponse({"message": "error", "body": "No data found for this user"}, status_code=404)

    turns = await redis.lrange(key, 0, -1)
    turns = [json.loads(turn.decode("utf-8")) for turn in turns[::-1]]
    data = {
        "type": "post_predict",
        "username": request.username,
        "name": request.name,
        "user_inputs": [turn.get("user_input") for turn in turns],
        "bot_responses": [turn.get("bot_response") for turn in turns]
    }

    if request.remove_history:
        await redis.delete(key)

    await websocket_client.send(data)
    response = await websocket_client.receive()

    if response.get("message") != "success":
        return JSONResponse({"message": "error", "body": "Failed to predict retrospective"}, status_code=422)
    
    await websocket_client.close()
    del websocket_client
    
    # notice_url = f"http://host.docker.internal:8000/api/{request.username}/notices/"
    # notice_url = f"http://main_app/api/{request.username}/notices/"
    # notice_url = f"http://localhost/api/{request.username}/notices/"
    notice_url = f"http://223.130.139.176/api/{request.username}/notices/"
    data = {
        "title": "알림",
        "text": "회고가 생성되었습니다. 지금 바로 회고탭에서 확인해보세요!",
        "retrospective_id": response.get("body").get("id") 
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(notice_url, json=data)
            response.raise_for_status() # object Response can't be used in 'await' expression
            if response.status_code != 201: # new entity created 
                return JSONResponse({"message": "error", "body": "Success to predict retrospective but failed to send notice"}, status_code=422)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    return JSONResponse({"message": "success"}, status_code=200)



@router.post("/retrospective/all")
async def predict_retrospective(redis: Redis = Depends(get_redis)):
    websocket_client = WebSocketClient(uri=config.retrospective_app_ws_url)
    websocket_client.handshake()

    # reading all exising user keys
    pattern = "chat_history:*"
    cursor = '0' # should be str 0
    matching_keys = []
    while cursor != 0: # should be int 0
        cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
        matching_keys.extend(keys)

    # get chat data for each user
    async for key in matching_keys:
        username = key.decode("utf-8").split(":")[1]
        name = await redis.get(f"username:{username}")

        turns = await redis.lrange(key, 0, -1)
        turns = [json.loads(turn.decode("utf-8")) for turn in turns[::-1]]
        data = {
            "type": "post_predict",
            "username": username,
            "name": name.decode("utf-8"),
            "user_inputs": [turn.get("user_input") for turn in turns],
            "bot_responses": [turn.get("bot_response") for turn in turns]
        }

        await websocket_client.send(data)
        response = await websocket_client.receive()

        if response.get("message") != "success":
            return JSONResponse({"message": "error", "body": f"Failed to predict retrospective of {data.get('username')}"}, status_code=422)

        await websocket_client.close()
        del websocket_client

    return JSONResponse({"message": "success"}, status_code=200)







