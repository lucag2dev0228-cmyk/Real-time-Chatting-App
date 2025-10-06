from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Conversation, Message, MessageReadStatus

User = get_user_model()


class ConversationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
    
    def test_create_direct_conversation(self):
        """Test creating a direct conversation"""
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.set([self.user1, self.user2])
        
        self.assertFalse(conversation.is_group)
        self.assertEqual(conversation.participant_count, 2)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())
    
    def test_create_group_conversation(self):
        """Test creating a group conversation"""
        conversation = Conversation.objects.create(
            name='Test Group',
            is_group=True
        )
        conversation.participants.set([self.user1, self.user2])
        
        self.assertTrue(conversation.is_group)
        self.assertEqual(conversation.name, 'Test Group')
        self.assertEqual(conversation.participant_count, 2)
    
    def test_conversation_str_representation(self):
        """Test conversation string representation"""
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.set([self.user1, self.user2])
        
        # The order might vary, so check that both names are present
        conversation_str = str(conversation)
        self.assertIn(self.user1.full_name, conversation_str)
        self.assertIn(self.user2.full_name, conversation_str)
        self.assertIn('&', conversation_str)
    
    def test_group_conversation_str_representation(self):
        """Test group conversation string representation"""
        conversation = Conversation.objects.create(
            name='Test Group',
            is_group=True
        )
        conversation.participants.set([self.user1, self.user2])
        
        self.assertEqual(str(conversation), 'Test Group')


class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        self.conversation = Conversation.objects.create(is_group=False)
        self.conversation.participants.set([self.user1, self.user2])
    
    def test_create_message(self):
        """Test creating a message"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, world!',
            message_type='text'
        )
        
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Hello, world!')
        self.assertEqual(message.message_type, 'text')
        self.assertFalse(message.is_edited)
    
    def test_message_to_dict(self):
        """Test message to_dict method"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, world!',
            message_type='text'
        )
        
        message_dict = message.to_dict()
        
        self.assertEqual(message_dict['id'], str(message.id))
        self.assertEqual(message_dict['conversation_id'], str(self.conversation.id))
        self.assertEqual(message_dict['sender_id'], str(self.user1.id))
        self.assertEqual(message_dict['sender_name'], self.user1.full_name)
        self.assertEqual(message_dict['content'], 'Hello, world!')
        self.assertEqual(message_dict['message_type'], 'text')
        self.assertFalse(message_dict['is_edited'])
        self.assertIsNone(message_dict['reply_to_id'])
    
    def test_message_str_representation(self):
        """Test message string representation"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, world!',
            message_type='text'
        )
        
        expected_str = f"{self.user1.full_name}: Hello, world!..."
        self.assertEqual(str(message), expected_str)
    
    def test_message_with_reply(self):
        """Test message with reply"""
        original_message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Original message',
            message_type='text'
        )
        
        reply_message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content='Reply message',
            message_type='text',
            reply_to=original_message
        )
        
        self.assertEqual(reply_message.reply_to, original_message)
        self.assertEqual(reply_message.to_dict()['reply_to_id'], str(original_message.id))


class MessageReadStatusModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        self.conversation = Conversation.objects.create(is_group=False)
        self.conversation.participants.set([self.user1, self.user2])
        
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Test message',
            message_type='text'
        )
    
    def test_create_message_read_status(self):
        """Test creating message read status"""
        read_status = MessageReadStatus.objects.create(
            message=self.message,
            user=self.user2
        )
        
        self.assertEqual(read_status.message, self.message)
        self.assertEqual(read_status.user, self.user2)
        self.assertIsNotNone(read_status.read_at)
    
    def test_message_read_status_str_representation(self):
        """Test message read status string representation"""
        read_status = MessageReadStatus.objects.create(
            message=self.message,
            user=self.user2
        )
        
        expected_str = f"{self.user2.full_name} read message {self.message.id}"
        self.assertEqual(str(read_status), expected_str)
    
    def test_message_read_status_unique_constraint(self):
        """Test that message read status is unique per message and user"""
        MessageReadStatus.objects.create(
            message=self.message,
            user=self.user2
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            MessageReadStatus.objects.create(
                message=self.message,
                user=self.user2
            )


class ConversationAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Create auth token
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_create_conversation_success(self):
        """Test successful conversation creation"""
        url = reverse('create_conversation')
        data = {
            'participant_ids': [str(self.user2.id)],
            'is_group': False
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)
        self.assertEqual(len(response.data['participants']), 2)
        self.assertFalse(response.data['is_group'])
    
    def test_create_group_conversation(self):
        """Test creating a group conversation"""
        url = reverse('create_conversation')
        data = {
            'participant_ids': [str(self.user2.id)],
            'name': 'Test Group',
            'is_group': True
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)
        self.assertEqual(response.data['name'], 'Test Group')
        self.assertTrue(response.data['is_group'])
    
    def test_get_conversations_list(self):
        """Test getting user's conversations"""
        # Create a conversation
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.set([self.user1, self.user2])
        
        url = reverse('conversations_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(conversation.id))
    
    def test_get_conversation_detail(self):
        """Test getting conversation details"""
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.set([self.user1, self.user2])
        
        url = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(conversation.id))
    
    def test_get_conversation_detail_unauthorized(self):
        """Test getting conversation details without being a participant"""
        user3 = User.objects.create_user(
            username="testuser3",
            email='user3@example.com',
            password='testpass123',
            first_name='User',
            last_name='Three'
        )
        
        conversation = Conversation.objects.create(is_group=False)
        conversation.participants.set([user3, self.user2])  # user1 is not a participant
        
        url = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthorized_access(self):
        """Test API access without authentication"""
        self.client.credentials()  # Remove auth
        
        url = reverse('conversations_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MessageAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser4",
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username="testuser5",
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        self.conversation = Conversation.objects.create(is_group=False)
        self.conversation.participants.set([self.user1, self.user2])
        
        # Create auth token
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_send_message_success(self):
        """Test successful message sending"""
        url = reverse('send_message')
        data = {
            'conversation_id': str(self.conversation.id),
            'content': 'Hello, world!',
            'message_type': 'text'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello, world!')
        self.assertEqual(response.data['sender']['id'], str(self.user1.id))
        self.assertEqual(response.data['message_type'], 'text')
    
    def test_send_message_unauthorized_conversation(self):
        """Test sending message to conversation user is not part of"""
        user3 = User.objects.create_user(
            username="testuser3",
            email='user3@example.com',
            password='testpass123',
            first_name='User',
            last_name='Three'
        )
        
        other_conversation = Conversation.objects.create(is_group=False)
        other_conversation.participants.set([user3, self.user2])  # user1 is not a participant
        
        url = reverse('send_message')
        data = {
            'conversation_id': str(other_conversation.id),
            'content': 'Hello, world!',
            'message_type': 'text'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_conversation_messages(self):
        """Test getting conversation messages"""
        # Create some messages
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Message 1'
        )
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content='Message 2'
        )
        
        url = reverse('conversation_messages', kwargs={'conversation_id': self.conversation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['messages']), 2)
    
    def test_get_conversation_messages_with_pagination(self):
        """Test getting conversation messages with pagination"""
        # Create multiple messages
        for i in range(5):
            Message.objects.create(
                conversation=self.conversation,
                sender=self.user1,
                content=f'Message {i}'
            )
        
        url = reverse('conversation_messages', kwargs={'conversation_id': self.conversation.id})
        response = self.client.get(url, {'limit': 3, 'offset': 0})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['messages']), 3)
    
    def test_mark_message_read(self):
        """Test marking a message as read"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content='Test message'
        )
        
        url = reverse('mark_message_read', kwargs={'message_id': message.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Message marked as read')
        
        # Check that read status was created
        read_status = MessageReadStatus.objects.get(message=message, user=self.user1)
        self.assertIsNotNone(read_status)
    
    def test_mark_message_read_unauthorized(self):
        """Test marking a message as read without being a conversation participant"""
        user3 = User.objects.create_user(
            username="testuser3",
            email='user3@example.com',
            password='testpass123',
            first_name='User',
            last_name='Three'
        )
        
        other_conversation = Conversation.objects.create(is_group=False)
        other_conversation.participants.set([user3, self.user2])
        
        message = Message.objects.create(
            conversation=other_conversation,
            sender=user3,
            content='Test message'
        )
        
        url = reverse('mark_message_read', kwargs={'message_id': message.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_unread_messages_count(self):
        """Test getting unread messages count"""
        # Create messages from user2 (user1 should have unread count)
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content='Message 1'
        )
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            content='Message 2'
        )
        
        url = reverse('unread_messages_count')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)
    
    def test_start_direct_chat(self):
        """Test starting a direct chat with another user"""
        url = reverse('start_direct_chat')
        data = {
            'user_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)
        self.assertFalse(response.data['is_group'])
        self.assertEqual(len(response.data['participants']), 2)
    
    def test_start_direct_chat_with_self(self):
        """Test starting a direct chat with yourself"""
        url = reverse('start_direct_chat')
        data = {
            'user_id': str(self.user1.id)
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Cannot start chat with yourself')
    
    def test_start_direct_chat_nonexistent_user(self):
        """Test starting a direct chat with non-existent user"""
        url = reverse('start_direct_chat')
        data = {
            'user_id': '00000000-0000-0000-0000-000000000000'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')
