import json
import logging
from typing import List, Optional

from redis import Redis as RedisType

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)

from langchain.utilities.redis import get_client

logger = logging.getLogger(__name__)

# from https://api.python.langchain.com/en/v0.0.343/_modules/langchain/memory/chat_message_histories/redis.html#RedisChatMessageHistory
class CustomRedisChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored in a Redis database."""
    def __init__(
        self,
        session_id: str,
        key_prefix: str = "message_store:",
        redis_client: RedisType = None,
        count: Optional[int] = None,
        ttl: Optional[int] = None,
    ):
        
        self.redis_client = redis_client
        self.session_id = session_id
        self.key_prefix = key_prefix
        self.count = count
        self.ttl = ttl


    @property
    def key(self) -> str:
        """Construct the record key to use"""
        return self.key_prefix + self.session_id

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from Redis"""
        if not self.count:
            _items = self.redis_client.lrange(self.key, 0, -1) # start index, end index (inclusive)
        else:
            _items = self.redis_client.lrange(self.key, 0, self.count - 1)
        items = [json.loads(m.decode("utf-8")) for m in _items[::-1]]
        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Redis"""
        self.redis_client.lpush(self.key, json.dumps(message_to_dict(message)))
        if self.ttl:
            self.redis_client.expire(self.key, self.ttl)


    def clear(self) -> None:
        """Clear session memory from Redis"""
        self.redis_client.delete(self.key)
