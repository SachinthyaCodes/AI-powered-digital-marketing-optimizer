import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, MessageSquare, Globe, TrendingUp } from 'lucide-react';
import api from '../services/api';

const ChatInterface = ({ serviceId = null, embedMode = false }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userName, setUserName] = useState('');
  const [chatStarted, setChatStarted] = useState(false);
  const [detectedLanguage, setDetectedLanguage] = useState('en');
  const [currentIntent, setCurrentIntent] = useState('general');
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize session
  useEffect(() => {
    if (!sessionId) {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
    }
  }, []);

  // Load existing chat history if session exists
  useEffect(() => {
    if (sessionId && serviceId) {
      loadChatHistory();
    }
  }, [sessionId, serviceId]);

  const loadChatHistory = async () => {
    try {
      const response = await api.get(`/api/chat/history/${sessionId}?service_id=${serviceId}`);
      if (response.data.history && response.data.history.length > 0) {
        setMessages(response.data.history.map(msg => ({
          id: `${msg.timestamp}_${msg.sender}`,
          text: msg.message,
          sender: msg.sender,
          timestamp: new Date(msg.timestamp),
          language: msg.language || 'en',
          intent: msg.intent || 'general'
        })));
        setChatStarted(true);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !serviceId || isLoading) return;

    // If chat hasn't started yet and no user name provided
    if (!chatStarted && !userName.trim()) {
      alert('Please enter your name to start chatting');
      return;
    }

    const userMessage = {
      id: `${Date.now()}_user`,
      text: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date(),
      language: detectedLanguage,
      intent: currentIntent
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    const messageToSend = inputMessage.trim();
    setInputMessage('');

    try {
      const payload = {
        message: messageToSend,
        service_id: serviceId,
        session_id: sessionId,
        user_name: userName || 'Guest'
      };

      const response = await api.post('/api/chat/send-message', payload);
      
      if (response.data.response) {
        const botMessage = {
          id: `${Date.now()}_bot`,
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(response.data.timestamp),
          language: response.data.detected_language || 'en',
          intent: response.data.intent || 'general'
        };

        setMessages(prev => [...prev, botMessage]);
        setDetectedLanguage(response.data.detected_language || 'en');
        setCurrentIntent(response.data.intent || 'general');
        
        if (!chatStarted) {
          setChatStarted(true);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message to chat
      const errorMessage = {
        id: `${Date.now()}_error`,
        text: 'Sorry, I encountered an error. Please try again or contact support.',
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

  const getLanguageDisplay = (lang) => {
    const languages = {
      'en': 'English',
      'si': 'සිංහල',
      'ta': 'தமிழ்',
      'mixed': 'Mixed'
    };
    return languages[lang] || lang;
  };

  const getIntentDisplay = (intent) => {
    const intents = {
      'greeting': '👋 Greeting',
      'product_inquiry': '🛍️ Products',
      'pricing': '💰 Pricing',
      'order_tracking': '📦 Orders',
      'delivery_info': '🚚 Delivery',
      'payment': '💳 Payment',
      'complaint': '❗ Issue',
      'general': '💬 General'
    };
    return intents[intent] || intent;
  };

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Welcome screen for new chat
  if (!chatStarted && !embedMode) {
    return (
      <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="flex-1 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full mx-4">
            <div className="text-center mb-6">
              <Bot className="h-16 w-16 text-blue-600 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-800 mb-2">
                MarketMatic Smart Assistant
              </h1>
              <p className="text-gray-600">
                I'm here to help you with product information, orders, and any questions you may have.
                I can understand English, Sinhala, and Tamil.
              </p>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Your Name (Optional)
                </label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="Enter your name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && setChatStarted(true)}
                />
              </div>
              
              <button
                onClick={() => setChatStarted(true)}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <MessageSquare className="h-4 w-4" />
                Start Chat
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col ${embedMode ? 'h-96' : 'h-screen'} bg-gray-50`}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="font-semibold text-gray-800">MarketMatic Assistant</h2>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Globe className="h-3 w-3" />
                  {getLanguageDisplay(detectedLanguage)}
                </span>
                <span>{getIntentDisplay(currentIntent)}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 bg-green-500 rounded-full"></div>
            <span className="text-xs text-gray-500">Online</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p>Start a conversation! I'm here to help.</p>
            <div className="text-sm mt-2">
              <p>Try asking:</p>
              <ul className="mt-1 text-blue-600">
                <li>• "What products do you sell?"</li>
                <li>• "මිල කීයද?" (What's the price?)</li>
                <li>• "How can I track my order?"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.isError
                  ? 'bg-red-100 text-red-800 border border-red-200'
                  : 'bg-white text-gray-800 shadow-sm border'
              }`}
            >
              <div className="flex items-start gap-2">
                {message.sender === 'bot' && !message.isError && (
                  <Bot className="h-4 w-4 mt-1 text-blue-600" />
                )}
                {message.sender === 'user' && (
                  <User className="h-4 w-4 mt-1" />
                )}
                <div className="flex-1">
                  <p className="text-sm">{message.text}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {formatTimestamp(message.timestamp)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm border rounded-lg px-4 py-2 max-w-xs">
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
      <div className="bg-white border-t px-4 py-3">
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (English, සිංහල, தமிழ்)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows="1"
              disabled={isLoading}
              style={{ minHeight: '40px' }}
            />
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>Press Enter to send • Shift+Enter for new line</span>
          {chatStarted && userName && (
            <span>Chatting as: {userName}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;