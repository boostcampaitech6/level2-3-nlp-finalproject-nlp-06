# yourapp/websocket_client.py
import asyncio
import websockets

class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        # Wait for a confirmation message
        confirmation = await self.websocket.recv()
        if confirmation == "Connection successful":
            print("WebSocket connection successfully established.")
            return True
        else:
            print("Failed to establish WebSocket connection.")
            return False

    async def send(self, message):
        if self.websocket is None or self.websocket.closed:
            connected = await self.connect()
            if not connected:
                return "Connection failed"
        await self.websocket.send(message)
        return await self.websocket.recv()

    def send_sync(self, message):
        return self.loop.run_until_complete(self.send(message))

# Global WebSocket client instance
# websocket_client = WebSocketClient("ws://localhost:10000/ws")