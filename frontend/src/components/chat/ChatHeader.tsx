import React from 'react';

interface Participant {
  id: string;
  full_name: string;
  email: string;
  is_online?: boolean;
}

interface Conversation {
  id: string;
  name?: string;
  participants: Participant[];
  last_message?: any;
  created_at: string;
  updated_at: string;
}

interface ChatHeaderProps {
  conversation: Conversation;
  isConnected: boolean;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ conversation, isConnected }) => {
  const getConversationTitle = (): string => {
    if (conversation.name) {
      return conversation.name;
    }
    
    if (conversation.participants && conversation.participants.length > 0) {
      if (conversation.participants.length === 1) {
        return conversation.participants[0].full_name;
      } else {
        return `${conversation.participants.length} participants`;
      }
    }
    
    return 'Unknown Conversation';
  };

  const getConnectionStatus = (): string => {
    return isConnected ? '🟢 Connected' : '🔴 Disconnected';
  };

  return (
    <div className="bg-[#2c3e50] border-b border-[#34495e] p-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-white">{getConversationTitle()}</h3>
          {conversation.participants && Array.isArray(conversation.participants) && (
            <div className="text-sm text-gray-400 mt-1">
              {conversation.participants.map((participant, index) => (
                <span key={participant.id}>
                  {participant.full_name}
                  {participant.is_online && ' 🟢'}
                  {index < conversation.participants.length - 1 && ', '}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="text-sm text-gray-400">
          {getConnectionStatus()}
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;
