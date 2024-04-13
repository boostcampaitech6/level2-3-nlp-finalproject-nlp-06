import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

from config import config
from uuid import UUID, uuid4

class UserPersona(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    username: str
    text: str
    embedding: List[float] = Field(sa_column=Column(Vector(768))) 
    # ko-sroberta-multitask maps sentences & paragraphs to a 768 dimensional dense vector space
    # openai embedding dim is 1536 in dafault model 'text-embedding-ada-002'
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


engine = create_async_engine(config.db_url, echo=True)


AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()