import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  error: string | null;
  sendMessage: (message: WebSocketMessage) => boolean;
  connect: () => void;
  disconnect: () => void;
}

const useWebSocket = (
  conversationId: string | null, 
  onMessage: (data: WebSocketMessage) => void
): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const maxReconnectAttempts = 5;
  const isConnecting = useRef<boolean>(false);

  const connect = useCallback((): void => {
    if (!conversationId) return;
    
    // Prevent multiple connections
    if (isConnecting.current || (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING))) {
      return;
    }

    isConnecting.current = true;

    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const token = localStorage.getItem('token');
      const qs = token ? `?token=${encodeURIComponent(token)}` : '';
      
      // Use environment variable for API URL or fallback to localhost
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
      const wsHost = apiUrl.replace('http://', '').replace('https://', '');
      const wsUrl = `${protocol}//${wsHost}/ws/chat/${conversationId}/${qs}`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected successfully');
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        isConnecting.current = false;
      };

      ws.current.onmessage = (event: MessageEvent) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          onMessage(data);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.current.onclose = (event: CloseEvent) => {
        console.log('WebSocket disconnected:', event.code, event.reason, 'Clean:', event.wasClean);
        setIsConnected(false);
        isConnecting.current = false;
        
        // Don't attempt to reconnect if it's a clean close (1000) or if we're already at max attempts
        if (event.code === 1000) {
          console.log('WebSocket closed cleanly');
          return;
        }
        
        if (reconnectAttempts.current >= maxReconnectAttempts) {
          console.log('Max reconnection attempts reached');
          setError('Failed to reconnect to chat server');
          return;
        }
        
        // Only attempt to reconnect if we're not already reconnecting
        if (!reconnectTimeoutRef.current) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          reconnectAttempts.current++;
          
          console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, delay);
        }
      };

      ws.current.onerror = (error: Event) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };

    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      isConnecting.current = false;
    }
  }, [conversationId, onMessage]);

  const disconnect = useCallback((): void => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (ws.current) {
      if (typeof ws.current.close === 'function') {
        ws.current.close(1000, 'User disconnected');
      }
      ws.current = null;
    }
    
    setIsConnected(false);
    reconnectAttempts.current = 0;
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage): boolean => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(JSON.stringify(message));
        return true;
      } catch (err) {
        console.error('Error sending WebSocket message:', err);
        return false;
      }
    } else {
      console.warn('WebSocket is not connected');
      return false;
    }
  }, []);

  // Connect when conversationId changes
  useEffect(() => {
    if (conversationId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [conversationId]); // Remove connect and disconnect from dependencies

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []); // Remove disconnect from dependencies

  return {
    isConnected,
    error,
    sendMessage,
    connect,
    disconnect,
  };
};

export default useWebSocket;
