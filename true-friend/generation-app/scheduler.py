from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx
from loguru import logger


scheduler = AsyncIOScheduler()

async def create_retrospective_for_all_user():
    url = "http://generation_app:8001/retrospective/all"
    try:
        response = await httpx.post(url)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    else:
        logger.info(f"Retrospective created successfully")