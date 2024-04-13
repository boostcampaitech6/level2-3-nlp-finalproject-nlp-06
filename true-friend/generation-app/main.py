from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from sqlmodel import SQLModel
from apscheduler.triggers.cron import CronTrigger

from config import config
from websocket import WebSocketClient
from database import connect_to_redis
from model import load_llm_chain
from api import router
from scheduler import scheduler, create_retrospective_for_all_user, test_timer



@asynccontextmanager
async def lifespan(app: FastAPI):
    # connect to redis
    logger.info("Connecting to Redis")
    app.state.redis = await connect_to_redis()

    logger.info("Ping to WebSocket servers")

    websocket_client = WebSocketClient(config.persona_app_ws_url)
    await websocket_client.handshake(retry=True)
    await websocket_client.close()

    websocket_client = WebSocketClient(config.retrospective_app_ws_url)
    await websocket_client.handshake(retry=True)
    await websocket_client.close()

    logger.info("Attaching scheduler")
    scheduler.add_job(
        create_retrospective_for_all_user, 
        CronTrigger(
            hour=config.retrospective_scheduler_hour,
            minute=config.retrospective_scheduler_minute,
            timezone="Asia/Seoul"
        )
    )
    scheduler.add_job(test_timer, 'interval', minutes=10)
    if not scheduler.running:
        scheduler.start()
    
    logger.info("Loading llm chain")
    load_llm_chain()
    
    yield

    logger.info("Disconnecting from Redis")
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router)

allowed_origins = [
    "http://localhost:8000",  # Allow frontend origin
    # Add any other origins as needed
    "http://main_app:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allowed_origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def root():
    return JSONResponse({"message": "This is the root of chat response service api."})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


