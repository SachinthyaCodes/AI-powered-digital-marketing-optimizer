import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, X, MessageCircle } from 'lucide-react';
import api from '../services/api';

const SimpleChatWidget = ({ serviceId, isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize session
  useEffect(() => {
    if (!sessionId) {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
    }
  }, []);

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history
  useEffect(() => {
    if (sessionId && serviceId && isOpen) {
      loadHistory();
    }
  }, [sessionId, serviceId, isOpen]);

  const loadHistory = async () => {
    try {
      const response = await api.get(`/api/chat/history/${sessionId}?service_id=${serviceId}`);
      if (response.data.history && response.data.history.length > 0) {
        setMessages(response.data.history.map(msg => ({
          id: `${msg.timestamp}_${msg.sender}`,
          text: msg.message,
          sender: msg.sender,
          timestamp: new Date(msg.timestamp)
        })));
      }
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !serviceId || isLoading) return;

    const userMessage = {
      id: `${Date.now()}_user`,
      text: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    const messageToSend = inputMessage.trim();
    setInputMessage('');

    try {
      const payload = {
        message: messageToSend,
        service_id: serviceId,
        session_id: sessionId
      };

      const response = await api.post('/api/chat/message', payload);
      
      if (response.data.response) {
        const botMessage = {
          id: `${Date.now()}_bot`,
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(response.data.timestamp)
        };

        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: `${Date.now()}_error`,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6" />
          <div>
            <h3 className="font-semibold">AI Assistant</h3>
            <p className="text-xs text-blue-100">Ask me anything about our business</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:bg-white/20 p-1 rounded"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">Hi! I can help you with:</p>
            <ul className="text-sm mt-2 text-blue-600 space-y-1">
              <li>• Product information & prices</li>
              <li>• FAQs and policies</li>
              <li>• General inquiries</li>
            </ul>
            <p className="text-xs text-gray-400 mt-2">Start typing below...</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : message.isError
                  ? 'bg-red-100 text-red-800 border border-red-200 rounded-bl-none'
                  : 'bg-white text-gray-800 shadow-sm border border-gray-200 rounded-bl-none'
              }`}
            >
              <div className="flex items-start gap-2">
                {message.sender === 'bot' && !message.isError && (
                  <Bot className="h-4 w-4 mt-0.5 text-blue-600 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm border border-gray-200 rounded-lg rounded-bl-none px-4 py-3 max-w-xs">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 text-blue-600" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-3 bg-white rounded-b-lg">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm"
            rows="2"
            disabled={isLoading}
          />
          
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-1">
          Press Enter to send
        </p>
      </div>
    </div>
  );
};

// Chat Button Component
export const ChatButton = ({ onClick }) => (
  <button
    onClick={onClick}
    className="fixed bottom-4 right-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-110 z-40"
  >
    <MessageCircle className="h-6 w-6" />
  </button>
);

export default SimpleChatWidget;
