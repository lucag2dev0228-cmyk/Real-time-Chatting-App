import React from 'react';
import { formatDistanceToNow } from 'date-fns';

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

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  onConversationSelect: (conversation: Conversation) => void;
  currentUserId: string;
}

const ConversationList: React.FC<ConversationListProps> = ({ 
  conversations, 
  selectedConversation, 
  onConversationSelect,
  currentUserId
}) => {
  // Ensure conversations is always an array
  const safeConversations = Array.isArray(conversations) ? conversations : [];

  const formatTime = (dateString: string): string => {
    if (!dateString) return '';
    return formatDistanceToNow(new Date(dateString), { addSuffix: true });
  };

  const getConversationName = (conversation: Conversation): string => {
    console.log('Getting conversation name for:', { 
      id: conversation.id, 
      name: conversation.name, 
      participants: conversation.participants?.map(p => ({ id: p.id, name: p.full_name })),
      currentUserId 
    });
    
    if (conversation.name) {
      return conversation.name;
    }
    
    if (conversation.participants && conversation.participants.length > 0) {
      // For 1:1 chats, show the other participant's name
      if (conversation.participants.length === 2) {
        // Find the participant who is not the current user
        const otherParticipant = conversation.participants.find(p => p.id !== currentUserId);
        console.log('Other participant found:', otherParticipant);
        return otherParticipant ? otherParticipant.full_name : 'Direct Chat';
      } else if (conversation.participants.length === 1) {
        return conversation.participants[0].full_name;
      } else if (conversation.participants.length > 2) {
        return 'Group Chat';
      }
    }
    
    return 'Unknown';
  };

  const getLastMessagePreview = (conversation: Conversation): string => {
    if (!conversation.last_message) {
      return 'No messages yet';
    }
    
    const message = conversation.last_message;
    const preview = message.content.length > 50 
      ? message.content.substring(0, 50) + '...'
      : message.content;
    
    return `${message.sender_name}: ${preview}`;
  };

  if (safeConversations.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-700 mb-2">No conversations</h3>
          <p className="text-gray-500">Start a new conversation to begin chatting!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {safeConversations.map((conversation) => (
        <div
          key={conversation.id}
          className={`p-4 border-b border-[#34495e] cursor-pointer hover:bg-[#485664] transition-colors ${
            selectedConversation?.id === conversation.id ? 'bg-[#5887b4] border-[#34495e]' : 'bg-[#2c3e50]'
          }`}
          onClick={() => onConversationSelect(conversation)}
        >
          <div className="flex justify-between items-start mb-2">
            <div className="font-medium text-white truncate">
              {getConversationName(conversation)}
            </div>
            {conversation.last_message && (
              <div className={`text-xs text-gray-400 ml-2 flex-shrink-0 ${selectedConversation?.id === conversation.id ? 'text-white' : 'text-gray-400'}`}>
                {formatTime(conversation.last_message.created_at)}
              </div>
            )}
          </div>
          <div className={`text-sm text-gray-400 truncate ${selectedConversation?.id === conversation.id ? 'text-white' : 'text-gray-400'}`}>
            {getLastMessagePreview(conversation)}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ConversationList;
