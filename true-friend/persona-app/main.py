from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from sqlmodel import SQLModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession    

import os
import json

from api import router
from config import config
from database import engine, UserPersona
from model import load_tf_model, load_embedding_model



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    logger.info(f"Creating database connection to {config.db_url}")
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector")) # DO NOT move to postgre_db initdb.sh
        try:
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Table created")
        except Exception as e:
            logger.error(f"Error creating table: {e}")

    logger.info(f"Load tansformers model {config.tf_model_id}")
    load_tf_model()

    logger.info("Load embeddings")
    load_embedding_model()

    # The server starts to recieve requests after yield
    yield

    # Clean up resources
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
def root():
    return JSONResponse({"message": "This is the root of persona extraction service api."})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True) # 8001 for redis stack