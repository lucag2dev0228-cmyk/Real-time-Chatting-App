from django.contrib import admin
from .models import Conversation, Message, MessageReadStatus


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group', 'participant_count', 'created_at', 'updated_at')
    list_filter = ('is_group', 'created_at')
    search_fields = ('name', 'participants__email', 'participants__first_name', 'participants__last_name')
    filter_horizontal = ('participants',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'content_preview', 'message_type', 'created_at', 'is_edited')
    list_filter = ('message_type', 'created_at', 'is_edited')
    search_fields = ('content', 'sender__email', 'sender__first_name', 'sender__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('read_at',)
























