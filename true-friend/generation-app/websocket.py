import websockets
import asyncio
import json
from collections import deque
from loguru import logger



class WebSocketClient:
    def __init__(self, uri, name="default"):
        self.connection = None
        self.uri = uri
        self.name = name

    async def connect(self):
        try:
            self.connection = await websockets.connect(self.uri)
            logger.info(f"Connected to {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to {self.uri}: {str(e)}")

    async def connect_with_retry(self, retry_interval=6, max_retries=5):
        for _ in range(max_retries):
            await self.connect()
            if self.connection:
                return
            else:
                logger.info(f"Retrying in {retry_interval} seconds")
                await asyncio.sleep(retry_interval)
        logger.error(f"Failed to connect to {self.uri} after {max_retries} retries")
    
    async def handshake(self, retry=False):
        if not retry:
            await self.connect()
        else:
            await self.connect_with_retry()
        response = await self.receive()
        if not response.get("message") == "Connection successful":
            logger.error(f"Failed to connect to {self.uri}: {response}")
            self.connection = None
    
    async def send(self, data):
        if self.connection:
            await self.connection.send(json.dumps(data))
            logger.info(f"Data sent")
        else:
            logger.error("Connection not found")
    
    async def receive(self):
        if self.connection:
            response = await self.connection.recv()
            logger.info(f"Response received")
            return json.loads(response)
        else:
            logger.error("Connection not found")
            return None
    
    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("Connection closed")
        else:
            logger.error("Connection not found")




