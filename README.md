# Real-time Chat Application

A modern, scalable real-time chat application built with Django, React, Redis, and WebSockets. This application provides instant messaging capabilities with user authentication, conversation management, and real-time message delivery.

## Features

### Core Features Implemented

#### **Real-time Messaging**
- **WebSocket Integration**: Real-time bidirectional communication using Django Channels
- **Instant Message Delivery**: Messages are delivered instantly to all conversation participants
- **Typing Indicators**: Real-time typing status for better user experience
- **Message Status**: Online/offline status tracking for users
- **Auto-reconnection**: Automatic WebSocket reconnection with exponential backoff

#### **User Management & Authentication**
- **Custom User Model**: Extended Django User model with additional fields (first_name, last_name, email)
- **Token-based Authentication**: Secure API authentication using Django REST Framework tokens
- **User Registration**: Complete registration flow with validation
- **User Login/Logout**: Secure authentication with session management
- **User Profile Management**: View and update user profiles
- **Online Status Tracking**: Real-time user online/offline status

#### **Conversation Management**
- **Direct Messages**: 1-on-1 private conversations
- **Group Conversations**: Multi-participant group chats (infrastructure ready)
- **Conversation History**: Persistent message storage and retrieval
- **Participant Management**: Add/remove users from conversations
- **Conversation Discovery**: Find existing conversations or create new ones

#### **Performance & Scalability**
- **Redis Integration**: Fast message storage and retrieval using Redis
- **Database Optimization**: Efficient PostgreSQL queries with proper indexing
- **Caching Strategy**: Redis-based caching for improved performance
- **Message TTL**: Automatic cleanup of old messages from Redis (7-day retention)

#### **API Rate Limiting & Security**
- **Rate Limiting**: Comprehensive API rate limiting using django-ratelimit
  - Registration: 5 requests per minute per IP
  - Login: 10 requests per minute per IP
  - Message sending: 30 requests per minute per user
  - Conversation creation: 10 requests per minute per user
  - Direct chat: 20 requests per minute per user
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **CSRF Protection**: Django's built-in CSRF protection
- **Input Validation**: Comprehensive form and API input validation

#### **Logging & Monitoring**
- **Comprehensive Logging**: Detailed logging for all API calls and system events
- **Structured Logging**: JSON-formatted logs for easy parsing and analysis
- **API Call Tracking**: Every API request is logged with user information
- **Error Tracking**: Detailed error logging with stack traces
- **Performance Monitoring**: Request timing and performance metrics

#### **Frontend Features**
- **Modern React UI**: Built with React 18 and TypeScript
- **Responsive Design**: Mobile-first responsive design using Tailwind CSS
- **Real-time Updates**: Live message updates and user status changes
- **Authentication Flow**: Complete login/register/logout flow
- **Error Handling**: Comprehensive error handling and user feedback

### Architecture

#### **Backend Architecture**
```
Django REST API
├── Authentication (Token-based)
├── WebSocket Consumers (Django Channels)
├── Database Layer (PostgreSQL)
├── Cache Layer (Redis)
├── Message Queue (Redis)
└── API Rate Limiting
```

#### **Frontend Architecture**
```
React Application
├── Context API (Authentication)
├── WebSocket Hook (Real-time communication)
├── Component Library (Reusable UI components)
├── Routing (React Router)
└── State Management (React Hooks)
```

#### **Data Flow**
1. **Message Sending**: Frontend → WebSocket → Django Consumer → Redis + PostgreSQL
2. **Message Receiving**: Redis → WebSocket → Frontend (real-time)
3. **Message History**: Frontend → REST API → PostgreSQL (on page load/refresh)
4. **User Status**: WebSocket → Redis → All connected clients

## Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Django REST Framework 3.14.0**: API framework
- **Django Channels 4.0.0**: WebSocket support
- **PostgreSQL 15**: Primary database
- **Redis 7**: Caching and message queue
- **Daphne**: ASGI server for WebSocket support
- **Gunicorn**: WSGI server for production

### Frontend
- **React 18.2.0**: UI framework
- **TypeScript 4.9.5**: Type safety
- **Tailwind CSS 3.4.0**: Styling
- **React Router 6.8.1**: Client-side routing
- **Axios 1.3.4**: HTTP client
- **React Hook Form 7.43.5**: Form management
- **React Hot Toast 2.4.0**: Notifications

### DevOps & Deployment
- **Docker & Docker Compose**: Containerization
- **Multi-stage Docker builds**: Optimized production images
- **Environment-based configuration**: Separate dev/prod configs
- **Health checks**: Container health monitoring
- **Volume management**: Persistent data storage

## Project Structure

```
Real-time Chat App/
├── backend/                    # Django backend
│   ├── accounts/              # User management app
│   │   ├── models.py         # Custom User model
│   │   ├── views.py          # Auth endpoints
│   │   ├── serializers.py    # Data serialization
│   │   └── urls.py           # Auth URL routing
│   ├── chat/                 # Chat functionality app
│   │   ├── models.py         # Conversation & Message models
│   │   ├── views.py          # Chat API endpoints
│   │   ├── consumers.py      # WebSocket consumers
│   │   ├── redis_service.py  # Redis operations
│   │   ├── serializers.py    # Chat data serialization
│   │   └── urls.py           # Chat URL routing
│   ├── chat_app/             # Django project settings
│   │   ├── settings.py       # Main configuration
│   │   ├── asgi.py          # ASGI configuration
│   │   └── urls.py          # Main URL routing
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container config
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── auth/        # Authentication components
│   │   │   ├── chat/        # Chat components
│   │   │   └── common/      # Shared components
│   │   ├── contexts/        # React contexts
│   │   ├── hooks/           # Custom React hooks
│   │   └── App.tsx          # Main app component
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile          # Frontend container config
├── docker-compose.yml       # Production Docker setup
├── docker-compose.dev.yml   # Development Docker setup
└── README.md               # This file
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.10+ (for local development)

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone git@github.com:lucag2dev0228-cmyk/Real-time-Chat-App.git
   cd Real-time-Chat-App
   ```

2. **Start the application**
   ```bash
   
   # manually with Docker Compose
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - WebSocket: ws://localhost:8001/ws/chat/

### Option 2: Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up environment variables
   cp env.example .env
   # Edit .env with your configuration
   
   # Run migrations
   python manage.py migrate
   
   # Start the server
   python manage.py runserver
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Start Redis and PostgreSQL**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   docker run -d -p 5432:5432 -e POSTGRES_DB=chat_app -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password postgres:15-alpine
   ```

## Configuration

Create a `.env` file in the backend directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database Configuration
DB_NAME=chat_app
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Frontend Configuration

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8001
```

## Testing

### Running Tests

```bash
# Backend tests
./run_test.sh
```

### Test Coverage

The application includes comprehensive test coverage for:
- User authentication and registration
- Message sending and receiving
- WebSocket connections
- API rate limiting
- Error handling scenarios

## Monitoring & Logging

### Log Files
- `backend/logs/django.log`: General Django application logs
- `backend/logs/api.log`: API-specific logs with request details

### Log Format
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "message": "API request received",
  "user": "user@example.com",
  "endpoint": "/api/chat/messages/",
  "method": "POST",
  "ip_address": "127.0.0.1"
}
```

### Health Checks
- Backend health: `GET /api/health/`
- Database connectivity: Automatic health checks
- Redis connectivity: Automatic health checks
