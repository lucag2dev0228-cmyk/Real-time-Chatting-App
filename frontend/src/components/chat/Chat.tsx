import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import NewConversationModal from './NewConversationModal';
import DirectChatModal from './DirectChatModal';
import axios from 'axios';
import toast from 'react-hot-toast';

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

const Chat: React.FC = () => {
  const { user, logout } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [showNewConversationModal, setShowNewConversationModal] = useState<boolean>(false);
  const [showDirectChatModal, setShowDirectChatModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Utility function to ensure conversations are unique
  const ensureUniqueConversations = (conversations: Conversation[]): Conversation[] => {
    const uniqueConversations = conversations.filter((conversation, index, self) => 
      index === self.findIndex(conv => conv.id === conversation.id)
    );
    
    console.log('Deduplication result:', {
      original: conversations.length,
      unique: uniqueConversations.length,
      conversations: uniqueConversations.map(c => ({ id: c.id, name: c.name || 'No name' }))
    });
    
    return uniqueConversations;
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  // Clean up duplicates on mount
  useEffect(() => {
    if (conversations.length > 0) {
      const uniqueConversations = ensureUniqueConversations(conversations);
      if (uniqueConversations.length !== conversations.length) {
        console.log('Cleaning up duplicates on mount');
        setConversations(uniqueConversations);
      }
    }
  }, [conversations.length]);

  // Debug effect to monitor conversations changes
  useEffect(() => {
    console.log('Conversations state changed:', conversations.map(c => ({ 
      id: c.id, 
      name: c.name, 
      participants: c.participants?.map(p => ({ id: p.id, name: p.full_name }))
    })));
  }, [conversations]);


  const fetchConversations = async (): Promise<void> => {
    try {
      const response = await axios.get('/api/chat/conversations/');
      
      // Ensure response.data is an array
      const conversationsData = Array.isArray(response.data) ? response.data : [];
      
      // Remove duplicates based on conversation ID
      const uniqueConversations = conversationsData.filter((conversation, index, self) => 
        index === self.findIndex(conv => conv.id === conversation.id)
      );
      
      setConversations(uniqueConversations);
      
      // Select first conversation if none selected
      if (uniqueConversations.length > 0 && !selectedConversation) {
        setSelectedConversation(uniqueConversations[0]);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
      toast.error('Failed to load conversations');
      // Ensure conversations is always an array even on error
      setConversations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleConversationSelect = (conversation: Conversation): void => {
    setSelectedConversation(conversation);
  };

  const handleNewConversation = (conversation: Conversation): void => {
    console.log('handleNewConversation called with conversation:', conversation);
    setConversations(prev => {
      const safePrev = Array.isArray(prev) ? prev : [];
      console.log('Current conversations before update:', safePrev.map(c => ({ id: c.id, name: c.name || 'No name' })));
      
      // Check if conversation already exists by ID
      const existingIndex = safePrev.findIndex(conv => conv.id === conversation.id);
      console.log('Existing conversation index by ID:', existingIndex);
      
      // Also check if conversation exists by participants (for 1:1 chats)
      const participantIds = conversation.participants?.map(p => p.id).sort() || [];
      const existingByParticipants = safePrev.findIndex(conv => {
        if (!conv.participants || conv.participants.length !== participantIds.length) return false;
        const convParticipantIds = conv.participants.map(p => p.id).sort();
        return convParticipantIds.every((id, index) => id === participantIds[index]);
      });
      console.log('Existing conversation index by participants:', existingByParticipants);
      
      if (existingIndex !== -1) {
        // Update existing conversation and move to top
        console.log('Updating existing conversation at index:', existingIndex);
        const updatedConversations = [...safePrev];
        updatedConversations[existingIndex] = conversation;
        const uniqueConversations = ensureUniqueConversations(updatedConversations);
        const sorted = uniqueConversations.sort((a, b) => 
          new Date(b.updated_at || b.last_message?.created_at || b.created_at).getTime() - 
          new Date(a.updated_at || a.last_message?.created_at || a.created_at).getTime()
        );
        console.log('Updated conversations after sort:', sorted.map(c => ({ id: c.id, name: c.name || 'No name' })));
        return sorted;
      } else if (existingByParticipants !== -1) {
        // Update existing conversation by participants and move to top
        console.log('Updating existing conversation by participants at index:', existingByParticipants);
        const updatedConversations = [...safePrev];
        updatedConversations[existingByParticipants] = conversation;
        const uniqueConversations = ensureUniqueConversations(updatedConversations);
        const sorted = uniqueConversations.sort((a, b) => 
          new Date(b.updated_at || b.last_message?.created_at || b.created_at).getTime() - 
          new Date(a.updated_at || a.last_message?.created_at || a.created_at).getTime()
        );
        console.log('Updated conversations after sort:', sorted.map(c => ({ id: c.id, name: c.name || 'No name' })));
        return sorted;
      } else {
        // Add new conversation to the top and ensure uniqueness
        console.log('Adding new conversation');
        const newConversations = [conversation, ...safePrev];
        const uniqueConversations = ensureUniqueConversations(newConversations);
        console.log('New conversations after deduplication:', uniqueConversations.map(c => ({ id: c.id, name: c.name || 'No name' })));
        return uniqueConversations;
      }
    });
    setSelectedConversation(conversation);
    setShowNewConversationModal(false);
    setShowDirectChatModal(false);
  };

  const handleMessageSent = (message: Message): void => {
    // Update the conversation's last message and move it to the top
    setConversations(prev => {
      const safePrev = Array.isArray(prev) ? prev : [];
      const updatedConversations = safePrev.map(conv => 
        conv.id === message.conversation_id 
          ? { ...conv, last_message: message, updated_at: message.created_at }
          : conv
      );
      
      // Ensure uniqueness and sort by updated_at to move the most recent conversation to the top
      const uniqueConversations = ensureUniqueConversations(updatedConversations);
      return uniqueConversations.sort((a, b) => 
        new Date(b.updated_at || b.last_message?.created_at || b.created_at).getTime() - 
        new Date(a.updated_at || a.last_message?.created_at || a.created_at).getTime()
      );
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading chat...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-100">
      <div className="w-[350px] shadow-lg flex flex-col bg-[#2c3e50] border-r border-[#1e2835]">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-white">Chat App</h2>
        </div>
        
        <div className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.first_name?.charAt(0).toUpperCase()}
              </div>
              <div>
                <h4 className="font-medium text-white">{user?.full_name}</h4>
                <p className="text-sm text-gray-400">{user?.email}</p>
              </div>
            </div>
            <button 
              className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
              onClick={logout}
            >
              Logout
            </button>
          </div>
        </div>

        <div className="mx-4 my-2 space-y-2">
          <button 
            className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            onClick={() => setShowDirectChatModal(true)}
          >
            💬 Direct Chat
          </button>
          <button 
            className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            onClick={() => setShowNewConversationModal(true)}
          >
            👥 Group Chat
          </button>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
              <p className="text-gray-500">Loading conversations...</p>
            </div>
          </div>
        ) : (
          <ConversationList
            conversations={conversations}
            selectedConversation={selectedConversation}
            onConversationSelect={handleConversationSelect}
            currentUserId={user?.id || ''}
          />
        )}
      </div>

      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <ChatWindow
            conversation={selectedConversation}
            onMessageSent={handleMessageSent}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-700 mb-2">Welcome to Chat!</h3>
              <p className="text-gray-500">Select a conversation or create a new one to start chatting.</p>
            </div>
          </div>
        )}
      </div>

      {showNewConversationModal && (
        <NewConversationModal
          onClose={() => setShowNewConversationModal(false)}
          onConversationCreated={handleNewConversation}
        />
      )}

      {showDirectChatModal && (
        <DirectChatModal
          onClose={() => setShowDirectChatModal(false)}
          onConversationCreated={handleNewConversation}
          currentUserId={user?.id || ''}
        />
      )}
    </div>
  );
};

export default Chat;
