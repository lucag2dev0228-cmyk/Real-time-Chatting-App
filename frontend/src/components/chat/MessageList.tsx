import React from 'react';
import { format } from 'date-fns';

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

interface MessageListProps {
  messages: Message[];
  currentUserId: string;
}

const MessageList: React.FC<MessageListProps> = ({ messages, currentUserId }) => {
  const formatMessageTime = (dateString: string): string => {
    return format(new Date(dateString), 'HH:mm');
  };

  const getMessageDate = (dateString: string): string => {
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  const groupMessagesByDate = (messages: Message[]): Record<string, Message[]> => {
    const groups: Record<string, Message[]> = {};
    
    messages.forEach(message => {
      const date = getMessageDate(message.created_at);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(message);
    });
    
    // Sort messages within each date group by time (oldest first)
    Object.keys(groups).forEach(date => {
      groups[date].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    });
    
    return groups;
  };

  const renderMessage = (message: Message): React.ReactElement => {
    const isOwnMessage = String(message.sender_id) === String(currentUserId);
    
    console.log(message);
    return (
      <div key={message.id} className={`flex mb-4 ${isOwnMessage ? 'justify-end' : 'justify-start'}`}>
        {!isOwnMessage && (
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold mr-3 flex-shrink-0">
            {message.sender_name ? message.sender_name.charAt(0).toUpperCase() : '?'}
          </div>
        )}
        
        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-3xl text-white ${
          isOwnMessage 
            ? 'bg-[#5887b4]' 
            : 'bg-[#2c3e50]'
        }`}>
          {!isOwnMessage && (
            <div className="text-sm font-medium text-white mb-1">
              {message.sender_name || 'Unknown User'}
            </div>
          )}
          <p className="text-base">{message.content}</p>
          <div className={`text-xs mt-1 ${
            isOwnMessage ? 'text-blue-100' : 'text-gray-400'
          }`}>
            {formatMessageTime(message.created_at)}
          </div>
        </div>
        
        {isOwnMessage && (
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold ml-3 flex-shrink-0">
            {message.sender_name ? message.sender_name.charAt(0).toUpperCase() : '?'}
          </div>
        )}
      </div>
    );
  };

  const renderDateSeparator = (date: string): React.ReactElement => (
    <div key={date} className="flex justify-center my-4">
      <div className="bg-[#2c3e50] text-white text-sm px-3 py-1 rounded-full">
        {date}
      </div>
    </div>
  );

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-700 mb-2">No messages yet</h3>
          <p className="text-gray-500">Start the conversation by sending a message!</p>
        </div>
      </div>
    );
  }

  const messageGroups = groupMessagesByDate(messages);
  const sortedDates = Object.keys(messageGroups).sort((a, b) => 
    new Date(a).getTime() - new Date(b).getTime()
  );

  return (
    <div className="space-y-2">
      {Array.isArray(sortedDates) && sortedDates.map(date => (
        <React.Fragment key={date}>
          {renderDateSeparator(date)}
          {Array.isArray(messageGroups[date]) && messageGroups[date].map(renderMessage)}
        </React.Fragment>
      ))}
    </div>
  );
};

export default MessageList;
