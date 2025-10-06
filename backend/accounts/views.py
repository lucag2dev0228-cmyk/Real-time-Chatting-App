import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django_ratelimit.decorators import ratelimit
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .models import User

logger = logging.getLogger('chat_app.api')


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@ratelimit(key='ip', rate='5/m', method='POST')
def register(request):
    """Register a new user"""
    logger.info(f"Registration attempt from IP: {request.META.get('REMOTE_ADDR')}")
    
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        logger.info(f"User registered successfully: {user.email}")
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Registration failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@ratelimit(key='ip', rate='10/m', method='POST')
def login_view(request):
    """Login user"""
    logger.info(f"Login attempt from IP: {request.META.get('REMOTE_ADDR')}")
    
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        # Update user online status
        user.is_online = True
        user.save()
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    logger.warning(f"Login failed: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user"""
    logger.info(f"User logout: {request.user.email}")
    
    # Update user online status
    request.user.is_online = False
    request.user.save()
    
    # Delete token
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    logger.info(f"Profile request from user: {request.user.email}")
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    """Get list of all users"""
    logger.info(f"Users list request from user: {request.user.email}")
    users = User.objects.all().order_by('-is_online', 'first_name')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)



