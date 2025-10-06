"""
Simple test settings for the chat application.
This file contains minimal settings for running basic unit tests without external dependencies.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'test-secret-key-for-testing-only'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
]

LOCAL_APPS = [
    'accounts',
    'chat',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chat_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chat_app.wsgi.application'
ASGI_APPLICATION = 'chat_app.asgi.application'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable static files collection during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Use test media root
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Disable file uploads during tests
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024  # 1MB

# Mock Redis URL for tests that don't need Redis
REDIS_URL = 'redis://localhost:6379/15'

# Use PostgreSQL for testing to match production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('TEST_DB_NAME', default='chat_app_test'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'TEST': {
            'NAME': 'chat_app_test',
        },
    }
}

# Enable migrations for proper database setup
# We need migrations to create the proper table structure
MIGRATION_MODULES = {}

# Use in-memory cache for tests (no Redis required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Disable rate limiting in tests
RATELIMIT_ENABLE = False
RATELIMIT_USE_CACHE = 'default'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable CORS for tests
CORS_ALLOW_ALL_ORIGINS = True

# Use test secret key
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable debug toolbar and other development tools
DEBUG = False

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable static files collection during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Use test media root
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

# Disable file uploads during tests
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024  # 1MB

# Use test allowed hosts
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Mock Redis URL for tests that don't need Redis
REDIS_URL = 'redis://localhost:6379/15'
