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

interface NewConversationModalProps {
  onClose: () => void;
  onConversationCreated: (conversation: Conversation) => void;
}

const NewConversationModal: React.FC<NewConversationModalProps> = ({ onClose, onConversationCreated }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [conversationName, setConversationName] = useState<string>('');
  const [isGroup, setIsGroup] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async (): Promise<void> => {
    try {
      const response = await axios.get('/api/auth/users/');
      // Ensure response.data is an array
      const usersData = Array.isArray(response.data) ? response.data : [];
      setUsers(usersData);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Failed to load users');
      // Ensure users is always an array even on error
      setUsers([]);
    }
  };

  const handleUserToggle = (userId: string): void => {
    setSelectedUsers(prev => {
      if (prev.includes(userId)) {
        return prev.filter(id => id !== userId);
      } else {
        return [...prev, userId];
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    
    if (selectedUsers.length === 0) {
      toast.error('Please select at least one user');
      return;
    }

    if (isGroup && !conversationName.trim()) {
      toast.error('Please enter a conversation name for group chats');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('/api/chat/conversations/create/', {
        participant_ids: selectedUsers,
        name: conversationName.trim() || null,
        is_group: isGroup,
      });

      onConversationCreated(response.data);
      toast.success('Conversation created successfully!');
    } catch (error) {
      console.error('Error creating conversation:', error);
      toast.error('Failed to create conversation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">New Conversation</h3>
            <button 
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              onClick={onClose}
            >
              ×
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={isGroup}
                onChange={(e) => setIsGroup(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Group Conversation</span>
            </label>
          </div>

          {isGroup && (
            <div>
              <label htmlFor="conversationName" className="block text-sm font-medium text-gray-700 mb-2">
                Conversation Name
              </label>
              <input
                type="text"
                id="conversationName"
                value={conversationName}
                onChange={(e) => setConversationName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter conversation name"
                required={isGroup}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Select Users</label>
            <div className="max-h-60 overflow-y-auto space-y-2">
              {Array.isArray(users) && users.map(user => (
                <div key={user.id} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(user.id)}
                    onChange={() => handleUserToggle(user.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                    {user.first_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">{user.full_name}</div>
                    <div className="text-sm text-gray-500 truncate">{user.email}</div>
                  </div>
                  {user.is_online && <div className="text-green-500">🟢</div>}
                </div>
              ))}
            </div>
          </div>

          <div className="flex space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading || selectedUsers.length === 0}
            >
              {loading ? 'Creating...' : 'Create Conversation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewConversationModal;
