import React, { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  onTyping: () => void;
  onStopTyping: () => void;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, onTyping, onStopTyping }) => {
  const [message, setMessage] = useState<string>('');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    const value = e.target.value;
    setMessage(value);

    // Handle typing indicators
    if (value.trim() && !isTyping) {
      setIsTyping(true);
      onTyping();
    }

    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Set new timeout to stop typing
    typingTimeoutRef.current = setTimeout(() => {
      if (isTyping) {
        setIsTyping(false);
        onStopTyping();
      }
    }, 1000);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault();
    
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
      
      // Stop typing indicator
      if (isTyping) {
        setIsTyping(false);
        onStopTyping();
      }
      
      // Clear timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="border-t border-[#34495e] bg-[#2c3e50] p-4">
      <form onSubmit={handleSubmit} className="flex space-x-3">
        <textarea
          value={message}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className="flex-1 px-3 py-2 border border-[#34495e] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={1}
          style={{
            minHeight: '40px',
            maxHeight: '120px',
            backgroundColor: '#2c3e50',
            color: 'white',
          }}
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          disabled={!message.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default MessageInput;
