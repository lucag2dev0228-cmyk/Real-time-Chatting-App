import json
import redis
from django.conf import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger('chat_app.api')


class RedisService:
    """Service for managing Redis operations for chat messages"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.message_ttl = 86400 * 7  # 7 days
    
    def store_message(self, message_data: Dict) -> bool:
        """Store message in Redis"""
        try:
            conversation_id = message_data['conversation_id']
            message_id = message_data['id']
            
            # Store message in conversation's message list
            key = f"conversation:{conversation_id}:messages"
            self.redis_client.lpush(key, json.dumps(message_data))
            
            # Set TTL for the conversation messages
            self.redis_client.expire(key, self.message_ttl)
            
            # Store individual message for quick access
            message_key = f"message:{message_id}"
            self.redis_client.setex(message_key, self.message_ttl, json.dumps(message_data))
            
            logger.info(f"Message stored in Redis: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing message in Redis: {str(e)}")
            return False
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get messages for a conversation from Redis"""
        try:
            key = f"conversation:{conversation_id}:messages"
            
            # Get messages from Redis
            messages_data = self.redis_client.lrange(key, offset, offset + limit - 1)
            
            messages = []
            for message_data in messages_data:
                try:
                    message = json.loads(message_data)
                    messages.append(message)
                except json.JSONDecodeError:
                    continue
            
            logger.info(f"Retrieved {len(messages)} messages from Redis for conversation {conversation_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving messages from Redis: {str(e)}")
            return []
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message from Redis"""
        try:
            message_key = f"message:{message_id}"
            message_data = self.redis_client.get(message_key)
            
            if message_data:
                return json.loads(message_data)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving message from Redis: {str(e)}")
            return None
    
    def delete_conversation_messages(self, conversation_id: str) -> bool:
        """Delete all messages for a conversation from Redis"""
        try:
            key = f"conversation:{conversation_id}:messages"
            self.redis_client.delete(key)
            
            logger.info(f"Deleted messages from Redis for conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting messages from Redis: {str(e)}")
            return False
    
    def get_conversation_message_count(self, conversation_id: str) -> int:
        """Get the number of messages in a conversation"""
        try:
            key = f"conversation:{conversation_id}:messages"
            return self.redis_client.llen(key)
        except Exception as e:
            logger.error(f"Error getting message count from Redis: {str(e)}")
            return 0
    
    def store_user_online_status(self, user_id: str, is_online: bool) -> bool:
        """Store user online status in Redis"""
        try:
            key = f"user:{user_id}:online"
            if is_online:
                self.redis_client.setex(key, 300, "1")  # 5 minutes TTL
            else:
                self.redis_client.delete(key)
            
            return True
        except Exception as e:
            logger.error(f"Error storing user online status: {str(e)}")
            return False
    
    def get_user_online_status(self, user_id: str) -> bool:
        """Get user online status from Redis"""
        try:
            key = f"user:{user_id}:online"
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error getting user online status: {str(e)}")
            return False
    
    def get_online_users(self) -> List[str]:
        """Get list of online user IDs"""
        try:
            pattern = "user:*:online"
            keys = self.redis_client.keys(pattern)
            user_ids = []
            for key in keys:
                user_id = key.decode('utf-8').split(':')[1]
                user_ids.append(user_id)
            return user_ids
        except Exception as e:
            logger.error(f"Error getting online users: {str(e)}")
            return []

























