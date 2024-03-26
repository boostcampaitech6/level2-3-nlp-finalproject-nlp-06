from sqlmodel import SQLModel, Field
from typing import Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

import datetime
from uuid import UUID, uuid4
from config import config


class Retrospective(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    username: str
    text: str
    comment: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


engine = create_async_engine(config.db_url, echo=False)


AsyncSessionLocal = async_sessionmaker(
    autoflush=False, autocommit=False, bind=engine, class_=AsyncSession
)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try: 
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
        finally:
            await session.close()