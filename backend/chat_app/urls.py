"""
URL configuration for chat_app project.
"""
from django.contrib import admin
from django.urls import path, include
from . import health_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/health/', health_views.health_check, name='health_check'),
]


