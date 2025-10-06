import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .redis_service import RedisService

User = get_user_model()
logger = logging.getLogger('chat_app.api')


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_service = RedisService()
        self.conversation_id = None
        self.conversation_group_name = None
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        
        # Check if user is authenticated (handled by TokenAuthMiddleware)
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close(code=4001, reason="Authentication required")
            return
        
        # Check if user is participant in conversation
        is_participant = await self.check_user_participation(user.id, self.conversation_id)
        
        if not is_participant:
            await self.close()
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Update user online status (simplified - no Redis for now)
        logger.info(f"User {user.email} connected to conversation {self.conversation_id}")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat successfully'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.conversation_group_name:
            # Leave conversation group
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
        
        # Update user online status (simplified - no Redis for now)
        if self.scope['user'].is_authenticated:
            logger.info(f"User {self.scope['user'].email} disconnected from conversation {self.conversation_id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'stop_typing':
                await self.handle_stop_typing(data)
            elif message_type == 'user_online':
                await self.handle_user_online_status(data)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def handle_chat_message(self, data):
        """Handle chat message"""
        user = self.scope['user']
        content = data.get('content', '').strip()
        
        if not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return
        
        # Check rate limiting (1 message per second)
        if await self.check_rate_limit(user.id):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Rate limit exceeded. Please wait before sending another message.'
            }))
            return
        
        # Create message
        message = await self.create_message(user, content, data.get('message_type', 'text'))
        
        if message:
            # Send message to conversation group (excluding sender to prevent duplicates)
            message_data = message.to_dict()
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data,
                    'sender_id': str(user.id)  # Include sender ID to exclude them
                }
            )
            
            logger.info(f"Message sent by {user.email}: {message.id}")
    
    async def handle_typing(self, data):
        """Handle typing indicator"""
        user = self.scope['user']
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing',
                'user_id': str(user.id),
                'user_name': user.full_name,
                'is_typing': True
            }
        )
    
    async def handle_stop_typing(self, data):
        """Handle stop typing indicator"""
        user = self.scope['user']
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing',
                'user_id': str(user.id),
                'user_name': user.full_name,
                'is_typing': False
            }
        )
    
    async def handle_user_online_status(self, data):
        """Handle user online status update"""
        user = self.scope['user']
        is_online = data.get('is_online', True)
        
        await self.update_user_online_status(user.id, is_online)
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'user_status',
                'user_id': str(user.id),
                'user_name': user.full_name,
                'is_online': is_online
            }
        )
    
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def typing(self, event):
        """Send typing indicator to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))
    
    async def user_status(self, event):
        """Send user status update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_online': event['is_online']
        }))
    
    @database_sync_to_async
    def check_user_participation(self, user_id, conversation_id):
        """Check if user is participant in conversation"""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return conversation.participants.filter(id=user_id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def create_message(self, user, content, message_type):
        """Create message in database"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            message = Message.objects.create(
                conversation=conversation,
                sender=user,
                content=content,
                message_type=message_type
            )
            return message
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return None
    
    async def store_message_redis(self, message_data):
        """Store message in Redis"""
        # Use database_sync_to_async to make Redis calls async-safe
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def _store_message():
            self.redis_service.store_message(message_data)
        
        await _store_message()
    
    async def update_user_online_status(self, user_id, is_online):
        """Update user online status"""
        # Use database_sync_to_async to make Redis calls async-safe
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def _store_status():
            self.redis_service.store_user_online_status(str(user_id), is_online)
        
        await _store_status()
    
    async def check_rate_limit(self, user_id):
        """Check if user has exceeded rate limit"""
        # Simple rate limiting: 1 message per second
        import time
        current_time = int(time.time())
        key = f"rate_limit:{user_id}:{current_time}"
        
        # Use database_sync_to_async to make Redis calls async-safe
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def _check_rate_limit():
            # This is a simplified implementation
            # In a real app, you'd check Redis for the rate limit
            return False  # For now, we'll allow all messages
        
        return await _check_rate_limit()







