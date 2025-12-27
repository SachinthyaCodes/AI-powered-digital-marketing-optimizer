import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MessageCircle, Send, Bot, ArrowLeft, Sparkles } from 'lucide-react';
import api from '../services/api';

export default function BusinessChatDemo() {
  const { serviceId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [businessInfo, setBusinessInfo] = useState(null);
  const messagesEndRef = useRef(null);

  // Initialize session
  useEffect(() => {
    console.log('BusinessChatDemo - Service ID from URL:', serviceId);
    if (!serviceId || serviceId === 'undefined') {
      console.error('Invalid service ID:', serviceId);
      alert('Invalid service ID. Please access this page from the admin dashboard.');
      navigate('/admin/dashboard');
      return;
    }
    const newSessionId = `demo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    loadBusinessInfo();
    showWelcomeMessage();
  }, [serviceId]);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load business information
  const loadBusinessInfo = async () => {
    if (!serviceId || serviceId === 'undefined') {
      console.error('Cannot load business info - invalid service ID');
      return;
    }
    try {
      const response = await api.get(`/api/chat/business-info/${serviceId}`);
      setBusinessInfo(response.data);
    } catch (error) {
      console.error('Error loading business info:', error);
      alert('Failed to load business information. Please try again.');
    }
  };

  // Show welcome message
  const showWelcomeMessage = () => {
    const welcomeMsg = {
      id: 'welcome',
      text: 'Hello! I\'m your AI business assistant powered by SinLlama. Ask me anything about our products, services, FAQs, or policies! (සිංහල භාෂාවෙන්ද අවශ්‍යයි)',
      sender: 'bot',
      timestamp: new Date()
    };
    setMessages([welcomeMsg]);
  };

  // Send message to chatbot
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMsg = {
      id: `user_${Date.now()}`,
      text: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    
    const messageToSend = inputMessage.trim();
    setInputMessage('');

    try {
      const response = await api.post('/api/chat/demo/message', {
        message: messageToSend,
        service_id: serviceId,
        session_id: sessionId
      });

      if (response.data.response) {
        const botMsg = {
          id: `bot_${Date.now()}`,
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(response.data.timestamp)
        };
        setMessages(prev => [...prev, botMsg]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg = {
        id: `error_${Date.now()}`,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Dashboard</span>
          </button>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h1 className="text-lg font-bold text-gray-900">Business Chatbot Demo</h1>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center">
                <Bot className="w-8 h-8 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold">AI Business Assistant</h2>
                <p className="text-indigo-100 text-sm flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Powered by SinLlama Modal AI
                </p>
              </div>
            </div>
            {businessInfo && (
              <div className="mt-4 p-3 bg-white/10 rounded-lg backdrop-blur-sm">
                <p className="text-sm text-indigo-100">
                  This chatbot knows about your business's products, FAQs, and policies
                </p>
              </div>
            )}
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50" style={{ height: 'calc(100% - 200px)' }}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                    message.sender === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-sm'
                      : message.isError
                      ? 'bg-red-100 text-red-800 rounded-bl-sm'
                      : 'bg-white text-gray-800 shadow-md rounded-bl-sm'
                  }`}
                >
                  {message.sender === 'bot' && !message.isError && (
                    <div className="flex items-center gap-2 mb-2">
                      <Bot className="w-4 h-4 text-indigo-600" />
                      <span className="text-xs font-medium text-indigo-600">AI Assistant</span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  <p className={`text-xs mt-2 ${
                    message.sender === 'user' ? 'text-indigo-200' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white shadow-md rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex items-center gap-3">
                    <Bot className="w-4 h-4 text-indigo-600" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 bg-white">
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about products, FAQs, or policies..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                  rows="2"
                  disabled={isLoading}
                />
                <p className="text-xs text-gray-500 mt-1 ml-1">
                  Press Enter to send • Shift+Enter for new line
                </p>
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-indigo-600 text-white p-4 rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Info Card */}
        <div className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-100">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-indigo-600" />
            About This Chatbot
          </h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start gap-2">
              <span className="text-indigo-600 mt-0.5">•</span>
              <span>Powered by <strong>SinLlama</strong> (Sinhala + English AI model) running on Modal</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-600 mt-0.5">•</span>
              <span>Trained on your business's <strong>FAQs, Products, and Policies</strong></span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-600 mt-0.5">•</span>
              <span>Supports <strong>English and Sinhala</strong> languages</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-indigo-600 mt-0.5">•</span>
              <span>Each business gets a <strong>unique customizable</strong> chatbot</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
