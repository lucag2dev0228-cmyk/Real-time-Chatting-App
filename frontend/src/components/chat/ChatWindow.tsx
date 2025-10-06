import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ChatHeader from './ChatHeader';
import useWebSocket from '../../hooks/useWebSocket';

interface Participant {
  id: string;
  full_name: string;
  email: string;
}

interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_name: string;
  content: string;
  message_type: string;
  created_at: string;
  updated_at: string;
  is_edited: boolean;
}

interface Conversation {
  id: string;
  name?: string;
  participants: Participant[];
  last_message?: Message;
  created_at: string;
  updated_at: string;
}

interface TypingUser {
  user_id: string;
  user_name: string;
}

interface WebSocketMessage {
  type: string;
  sender_id?: string;
  message?: Message;
  user_id?: string;
  user_name?: string;
  is_typing?: boolean;
  [key: string]: any;
}

interface ChatWindowProps {
  conversation: Conversation;
  onMessageSent: (message: Message) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversation, onMessageSent }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const fetchMessages = async (): Promise<void> => {
    try {
      setLoading(true);
      const response = await fetch(`/api/chat/conversations/${conversation.id}/messages/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = (): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleWebSocketMessage = (data: WebSocketMessage): void => {
    switch (data.type) {
      case 'chat_message':
        // Only add message if it's not from the current user (prevent duplicates)
        if (data.sender_id && String(data.sender_id) !== String(user?.id)) {
          setMessages(prev => {
            const messageExists = prev.some(msg => msg.id === data.message?.id);
            if (!messageExists && data.message) {
              return [...prev, data.message];
            }
            return prev;
          });
          if (data.message) {
            onMessageSent(data.message);
          }
        }
        break;
      case 'typing':
        if (data.is_typing) {
          setTypingUsers(prev => {
            if (!prev.find(u => u.user_id === data.user_id)) {
              return [...prev, { user_id: data.user_id!, user_name: data.user_name! }];
            }
            return prev;
          });
        } else {
          setTypingUsers(prev => prev.filter(u => u.user_id !== data.user_id));
        }
        break;
      case 'user_status':
        // Handle user online/offline status
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const { sendMessage, isConnected } = useWebSocket(
    conversation.id,
    handleWebSocketMessage
  );

  useEffect(() => {
    fetchMessages();
  }, [conversation.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string): Promise<void> => {
    if (!content.trim()) return;

    try {
      const response = await fetch('/api/chat/messages/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          conversation_id: conversation.id,
          sender_id: user?.id,
          content: content.trim(),
          message_type: 'text',
        }),
      });

      if (response.ok) {
        const newMessage: Message = await response.json();
        setMessages(prev => [...prev, newMessage]);
        onMessageSent(newMessage);
        
        // Send via WebSocket for real-time delivery
        sendMessage({
          type: 'chat_message',
          content: content.trim(),
          message_type: 'text',
        });
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleTyping = (): void => {
    sendMessage({ type: 'typing' });
  };

  const handleStopTyping = (): void => {
    sendMessage({ type: 'stop_typing' });
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading messages...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <ChatHeader 
        conversation={conversation} 
        isConnected={isConnected}
      />
      
      <div className="flex-1 overflow-y-auto p-4 bg-[#1d2c3b]">
        <MessageList 
          messages={messages}
          currentUserId={user?.id || ''}
        />
        
        {Array.isArray(typingUsers) && typingUsers.length > 0 && (
          <div className="p-2 text-sm text-gray-500 italic">
            {typingUsers.map((typingUser, index) => (
              <span key={typingUser.user_id}>
                {typingUser.user_name} is typing
                {index < typingUsers.length - 1 && ', '}
              </span>
            ))}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <MessageInput
        onSendMessage={handleSendMessage}
        onTyping={handleTyping}
        onStopTyping={handleStopTyping}
      />
    </div>
  );
};

export default ChatWindow;