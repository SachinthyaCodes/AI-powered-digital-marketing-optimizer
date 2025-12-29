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
    <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200/50 animate-slide-in-right">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-2xl flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">AI Assistant</h3>
            <p className="text-xs text-blue-100">Powered by SinLlama</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:bg-white/20 p-2 rounded-xl transition-all hover:rotate-90"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar" style={{ background: 'linear-gradient(to bottom, #f9fafb, #f3f4f6)' }}>
        {messages.length === 0 && (
          <div className="text-center mt-8 animate-fade-in-up">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Bot className="h-8 w-8 text-white" />
            </div>
            <p className="text-sm font-semibold text-gray-900 mb-3">Welcome! How can I help you?</p>
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-gray-200/50 shadow-sm">
              <p className="text-sm text-gray-600 mb-2 font-medium">I can assist with:</p>
              <ul className="text-sm text-left space-y-2">
                <li className="flex items-center gap-2 text-blue-600">
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                  Product information & pricing
                </li>
                <li className="flex items-center gap-2 text-purple-600">
                  <span className="w-1.5 h-1.5 bg-purple-600 rounded-full"></span>
                  FAQs and policies
                </li>
                <li className="flex items-center gap-2 text-indigo-600">
                  <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full"></span>
                  General inquiries
                </li>
              </ul>
            </div>
            <p className="text-xs text-gray-500 mt-3">Start typing below to begin...</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <div
              className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                message.sender === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-br-md shadow-md'
                  : message.isError
                  ? 'bg-red-50 text-red-800 border border-red-200 rounded-bl-md shadow-sm'
                  : 'bg-white text-gray-800 shadow-md border border-gray-200/50 rounded-bl-md'
              }`}
            >
              <div className="flex items-start gap-2">
                {message.sender === 'bot' && !message.isError && (
                  <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Bot className="h-3.5 w-3.5 text-white" />
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  <p className={`text-xs mt-1.5 ${
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
          <div className="flex justify-start animate-fade-in">
            <div className="bg-white shadow-md border border-gray-200/50 rounded-2xl rounded-bl-md px-4 py-3 max-w-xs">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Bot className="h-3.5 w-3.5 text-white" />
                </div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200/50 p-4 bg-white/80 backdrop-blur-sm rounded-b-2xl">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none text-sm transition-all bg-white shadow-sm"
            rows="2"
            disabled={isLoading}
          />
          
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg hover:scale-105 active:scale-95"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        
        <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
          <span className="inline-block w-1 h-1 bg-green-500 rounded-full animate-pulse"></span>
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

// Chat Button Component
export const ChatButton = ({ onClick }) => (
  <button
    onClick={onClick}
    className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-2xl shadow-2xl hover:shadow-glow-purple transition-all hover:scale-110 active:scale-95 z-40 animate-fade-in group"
    aria-label="Open chat"
  >
    <MessageCircle className="h-7 w-7 group-hover:rotate-12 transition-transform" />
    <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white animate-pulse"></span>
  </button>
);

export default SimpleChatWidget;
