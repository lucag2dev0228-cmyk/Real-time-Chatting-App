import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_online?: boolean;
}

interface Conversation {
  id: string;
  name?: string;
  participants: User[];
  last_message?: any;
  created_at: string;
  updated_at: string;
}

interface DirectChatModalProps {
  onClose: () => void;
  onConversationCreated: (conversation: Conversation) => void;
  currentUserId: string;
}

const DirectChatModal: React.FC<DirectChatModalProps> = ({ onClose, onConversationCreated, currentUserId }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async (): Promise<void> => {
    try {
      const response = await axios.get('/api/auth/users/');
      const usersData = Array.isArray(response.data) ? response.data : [];
      setUsers(usersData);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Failed to load users');
      setUsers([]);
    }
  };

  const handleStartChat = async (user: User): Promise<void> => {
    try {
      setLoading(true);
      console.log('Starting chat with user:', user);
      console.log('Sending user_id to API:', user.id);
      const response = await axios.post('/api/chat/conversations/direct-chat/', {
        user_id: user.id
      });
      onConversationCreated(response.data);
      onClose();
      toast.success(`Started chat with ${user.full_name}`);
    } catch (error: any) {
      console.error('Error starting direct chat:', error);
      const errorMessage = error.response?.data?.error || 'Failed to start chat';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user => 
    user.id !== currentUserId && (
      user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Start Direct Chat</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="max-h-96 overflow-y-auto">
          {filteredUsers.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              {searchTerm ? 'No users found' : 'No users available'}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredUsers.map(user => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer border border-gray-200"
                  onClick={() => handleStartChat(user)}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">{user.full_name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {user.is_online && (
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    )}
                    <button
                      className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 disabled:opacity-50"
                      disabled={loading}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartChat(user);
                      }}
                    >
                      {loading ? 'Starting...' : 'Chat'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DirectChatModal;
