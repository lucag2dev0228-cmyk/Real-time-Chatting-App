import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Chat from './components/chat/Chat';
import ProtectedRoute from './components/common/ProtectedRoute';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route 
            path="/chat" 
            element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/chat" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  );
};

export default App;
