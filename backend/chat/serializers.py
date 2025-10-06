from rest_framework import serializers
from .models import Conversation, Message, MessageReadStatus
from accounts.serializers import UserSerializer


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participants = UserSerializer(many=True, read_only=True)
    participant_count = serializers.ReadOnlyField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'name', 'participants', 'participant_count', 'created_at', 
                 'updated_at', 'is_group', 'last_message')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': str(last_msg.id),
                'content': last_msg.content,
                'sender': last_msg.sender.full_name,
                'sender_name': last_msg.sender.full_name,
                'created_at': last_msg.created_at,
                'message_type': last_msg.message_type,
            }
        return None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages"""
    sender = UserSerializer(read_only=True)
    sender_name = serializers.SerializerMethodField()
    sender_id = serializers.SerializerMethodField()
    conversation_id = serializers.UUIDField(write_only=True)
    reply_to_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'sender_name', 'sender_id', 'conversation_id', 
                 'content', 'message_type', 'created_at', 'updated_at', 'is_edited', 
                 'reply_to', 'reply_to_id')
        read_only_fields = ('id', 'sender', 'conversation', 'created_at', 'updated_at', 'is_edited')

    def create(self, validated_data):
        # Remove write-only fields
        conversation_id = validated_data.pop('conversation_id')
        reply_to_id = validated_data.pop('reply_to_id', None)

        # Set the actual objects
        validated_data['conversation_id'] = conversation_id
        if reply_to_id:
            validated_data['reply_to_id'] = reply_to_id

        return super().create(validated_data)
    
    def get_sender_name(self, obj):
        """Get the sender's full name"""
        return obj.sender.full_name if obj.sender else None
    
    def get_sender_id(self, obj):
        """Get the sender's ID"""
        return str(obj.sender.id) if obj.sender else None


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """Serializer for message read status"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageReadStatus
        fields = ('message', 'user', 'read_at')
        read_only_fields = ('read_at',)


class CreateConversationSerializer(serializers.Serializer):
    """Serializer for creating conversations"""
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=10
    )
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_group = serializers.BooleanField(default=False)

    def validate_participant_ids(self, value):
        from accounts.models import User
        # Check if all participants exist
        existing_users = User.objects.filter(id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("One or more participants do not exist")
        return value



