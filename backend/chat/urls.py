from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.conversations_list, name='conversations_list'),
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/direct-chat/', views.start_direct_chat, name='start_direct_chat'),
    path('conversations/<uuid:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<uuid:conversation_id>/messages/', views.conversation_messages, name='conversation_messages'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<uuid:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    path('messages/unread-count/', views.unread_messages_count, name='unread_messages_count'),
]



