from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from loguru import logger

from api import router
from database import engine, Retrospective
from model import load_tf_model, load_llm_chains
from config import config

import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    logger.info(f"DB_USERNAME: {os.environ.get('DB_USERNAME')}")
    logger.info(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")
    logger.info(f"DB_HOST: {os.environ.get('DB_HOST')}")
    logger.info(f"DB_NAME: {os.environ.get('DB_NAME')}")

    logger.info(f"Creating database connection to {config.db_url}")
    async with engine.begin() as conn:
        try:
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Table created")
        except Exception as e:
            logger.error(f"Error creaing table: {e}")

    logger.info(f"Loading transformers model {config.tf_model_id}")
    load_tf_model()
    
    logger.info("Loading llm chain")
    load_llm_chains()

    yield

    logger.info("Shutting down")
    await engine.dispose()



app = FastAPI(lifespan=lifespan)
app.include_router(router=router)

allowed_origins = [
    "http://localhost:8001",
    "http://generation_app:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


@app.get("/")
async def root():
    return JSONResponse(content={"message": "This is the root of retrospective service api."}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)