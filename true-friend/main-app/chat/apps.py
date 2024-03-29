from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.core.signals import request_started, request_finished

import asyncio


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'Chat'

    # def ready(self):
    #     from .websocket_client import websocket_client
    #     from django.core.signals import request_started, request_finished

    #     # Connect the WebSocket
    #     asyncio.get_event_loop().run_until_complete(websocket_client.connect())

    #     # Register the shutdown signal
    #     request_finished.connect(self.shutdown_handler)

    # def shutdown_handler(self, **kwargs):
    #     from .websocket_client import websocket_client

    #     # Close the WebSocket connection
    #     tasks = [websocket_client.websocket.close()]
    #     asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))
