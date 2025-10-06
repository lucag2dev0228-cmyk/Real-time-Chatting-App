import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_ratelimit.decorators import ratelimit
from .models import Conversation, Message, MessageReadStatus
from .serializers import (
    ConversationSerializer, MessageSerializer, CreateConversationSerializer,
    MessageReadStatusSerializer
)
from .redis_service import RedisService
from accounts.models import User

logger = logging.getLogger('chat_app.api')
redis_service = RedisService()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversations_list(request):
    """Get list of user's conversations"""
    logger.info(f"Conversations list request from user: {request.user.email}")
    
    conversations = request.user.conversations.all()
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', method='POST')
def create_conversation(request):
    """Create a new conversation"""
    logger.info(f"Create conversation request from user: {request.user.email}")
    
    serializer = CreateConversationSerializer(data=request.data)
    if serializer.is_valid():
        participant_ids = serializer.validated_data['participant_ids']
        name = serializer.validated_data.get('name', '')
        is_group = serializer.validated_data.get('is_group', False)
        
        # Add current user to participants
        participant_ids.append(request.user.id)
        
        # Check if conversation already exists (for 1-on-1 chats)
        if not is_group and len(participant_ids) == 2:
            existing_conversation = Conversation.objects.filter(
                participants__in=participant_ids,
                is_group=False
            ).distinct().first()
            
            if existing_conversation and existing_conversation.participants.count() == 2:
                logger.info(f"Existing conversation found: {existing_conversation.id}")
                return Response(ConversationSerializer(existing_conversation).data)
        
        # Create new conversation
        conversation = Conversation.objects.create(
            name=name,
            is_group=is_group
        )
        conversation.participants.set(participant_ids)
        
        logger.info(f"New conversation created: {conversation.id}")
        return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Create conversation failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, conversation_id):
    """Get conversation details"""
    logger.info(f"Conversation detail request from user: {request.user.email}")
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is participant
    if request.user not in conversation.participants.all():
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ConversationSerializer(conversation)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    """Get messages for a conversation"""
    logger.info(f"Messages request from user: {request.user.email} for conversation: {conversation_id}")
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is participant
    if request.user not in conversation.participants.all():
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get pagination parameters
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    
    # Try to get messages from Redis first
    redis_messages = redis_service.get_conversation_messages(str(conversation_id), limit, offset)
    
    if redis_messages:
        logger.info(f"Retrieved {len(redis_messages)} messages from Redis")
        return Response({'messages': redis_messages})
    
    # Fallback to database
    messages = conversation.messages.all()[offset:offset + limit]
    serializer = MessageSerializer(messages, many=True)
    
    logger.info(f"Retrieved {len(messages)} messages from database")
    return Response({'messages': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='30/m', method='POST')
def send_message(request):
    """Send a message"""
    logger.info(f"Send message request from user: {request.user.email}")
    
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        conversation_id = serializer.validated_data['conversation_id']
        content = serializer.validated_data['content']
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is participant
        if request.user not in conversation.participants.all():
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            message_type=serializer.validated_data.get('message_type', 'text')
        )
        
        # Store in Redis
        message_data = message.to_dict()
        redis_service.store_message(message_data)
        
        # Update conversation timestamp
        conversation.save()
        
        logger.info(f"Message sent: {message.id}")
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Send message failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_read(request, message_id):
    """Mark a message as read"""
    logger.info(f"Mark message read request from user: {request.user.email}")
    
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user is participant in conversation
    if request.user not in message.conversation.participants.all():
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    # Create or update read status
    read_status, created = MessageReadStatus.objects.get_or_create(
        message=message,
        user=request.user
    )
    
    if created:
        logger.info(f"Message marked as read: {message_id}")
        return Response({'message': 'Message marked as read'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Message already marked as read'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_messages_count(request):
    """Get count of unread messages for user"""
    logger.info(f"Unread messages count request from user: {request.user.email}")
    
    # Get all conversations user is part of
    conversations = request.user.conversations.all()
    
    unread_count = 0
    for conversation in conversations:
        # Get messages user hasn't read
        unread_messages = conversation.messages.exclude(
            read_status__user=request.user
        ).exclude(sender=request.user)
        
        unread_count += unread_messages.count()
    
    return Response({'unread_count': unread_count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='20/m', method='POST')
def start_direct_chat(request):
    """Start a direct 1:1 chat with another user"""
    logger.info(f"Start direct chat request from user: {request.user.email}")
    
    target_user_id = request.data.get('user_id')
    if not target_user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        target_user = User.objects.get(id=target_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is trying to chat with themselves
    if target_user.id == request.user.id:
        return Response({'error': 'Cannot start chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if conversation already exists (exact 1:1 match)
    logger.info(f"Looking for existing conversation between {request.user.email} and {target_user.email}")
    existing_conversation = Conversation.objects.filter(
        participants=request.user.id,
        is_group=False
    ).filter(
        participants=target_user.id
    ).annotate(
        participant_count=Count('participants')
    ).filter(
        participant_count=2
    ).first()
    
    if existing_conversation:
        logger.info(f"Existing direct chat found: {existing_conversation.id} with participants: {[p.email for p in existing_conversation.participants.all()]}")
        return Response(ConversationSerializer(existing_conversation).data)
    
    # Create new direct conversation
    conversation = Conversation.objects.create(
        is_group=False
    )
    conversation.participants.set([request.user, target_user])
    
    logger.info(f"New direct chat created: {conversation.id} with participants: {[p.email for p in conversation.participants.all()]}")
    return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)



