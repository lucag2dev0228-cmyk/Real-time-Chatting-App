from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class Conversation(models.Model):
    """Model for chat conversations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group = models.BooleanField(default=False)

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group and self.name:
            return self.name
        elif self.participants.count() == 2:
            participants = list(self.participants.all())
            return f"{participants[0].full_name} & {participants[1].full_name}"
        return f"Conversation {self.id}"

    @property
    def participant_count(self):
        return self.participants.count()


class Message(models.Model):
    """Model for chat messages"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, default='text', choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.full_name}: {self.content[:50]}..."

    def to_dict(self):
        """Convert message to dictionary for Redis storage"""
        return {
            'id': str(self.id),
            'conversation_id': str(self.conversation.id),
            'sender_id': str(self.sender.id),
            'sender_name': self.sender.full_name,
            'content': self.content,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat(),
            'is_edited': self.is_edited,
            'reply_to_id': str(self.reply_to.id) if self.reply_to else None,
        }


class MessageReadStatus(models.Model):
    """Model to track message read status"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_read_status')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_read_status'
        unique_together = ['message', 'user']

    def __str__(self):
        return f"{self.user.full_name} read message {self.message.id}"










