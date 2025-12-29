import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MessageCircle, Send, Bot, ArrowLeft, Sparkles, X, MinusCircle, Info, Zap } from 'lucide-react';
import api from '../services/api';

export default function BusinessChatDemo() {
  const { serviceId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [businessInfo, setBusinessInfo] = useState(null);
  const [showInfo, setShowInfo] = useState(false);
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
      text: 'Hello! 👋 I\'m your AI business assistant. I can help you with:\n\n• Product information and recommendations\n• Frequently asked questions\n• Business policies and procedures\n• Services and pricing\n\nFeel free to ask me anything in English or Sinhala! සිංහලෙන් ද විමසන්න පුළුවන්!',
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

      console.log('Chat response:', response.data);

      if (response.data && response.data.bot_response) {
        const botMsg = {
          id: `bot_${Date.now()}`,
          text: response.data.bot_response,
          sender: 'bot',
          timestamp: response.data.timestamp ? new Date(response.data.timestamp) : new Date()
        };
        console.log('Adding bot message:', botMsg);
        setMessages(prev => [...prev, botMsg]);
      } else {
        console.error('No response in data:', response.data);
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Top Navigation Bar */}
      <nav className="bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Back Button */}
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100/80 transition-all group"
            >
              <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              <span className="font-medium hidden sm:inline">Dashboard</span>
            </button>

            {/* Title */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent hidden sm:block">
                AI Assistant
              </h1>
            </div>

            {/* Info Button */}
            <button
              onClick={() => setShowInfo(!showInfo)}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-100/80 transition-all"
            >
              <Info className="w-5 h-5" />
              <span className="font-medium hidden sm:inline">About</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden flex flex-col" style={{ height: 'calc(100vh - 180px)' }}>
              {/* Chat Header */}
              <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 px-6 py-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center ring-2 ring-white/30">
                      <Bot className="w-7 h-7 text-white" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-white">AI Business Assistant</h2>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                        <span className="text-xs text-blue-100">Online & Ready</span>
                      </div>
                    </div>
                  </div>
                  <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg border border-white/30">
                    <Zap className="w-4 h-4 text-yellow-300" />
                    <span className="text-xs font-medium text-white">Powered by SinLlama</span>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-gray-50 to-white custom-scrollbar">
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <div className={`flex gap-3 max-w-[85%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                        {/* Avatar */}
                        {message.sender === 'bot' && (
                          <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                            <Bot className="w-5 h-5 text-white" />
                          </div>
                        )}
                        {message.sender === 'user' && (
                          <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-gray-600 to-gray-700 rounded-lg flex items-center justify-center shadow-md">
                            <span className="text-white text-sm font-semibold">You</span>
                          </div>
                        )}

                        {/* Message Bubble */}
                        <div className="flex flex-col">
                          <div
                            className={`px-4 py-3 rounded-2xl shadow-sm ${
                              message.sender === 'user'
                                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-sm'
                                : message.isError
                                ? 'bg-red-50 text-red-800 border border-red-200 rounded-tl-sm'
                                : 'bg-white text-gray-800 border border-gray-200 rounded-tl-sm'
                            }`}
                          >
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                          </div>
                          <span className={`text-xs mt-1 px-1 ${
                            message.sender === 'user' ? 'text-right text-gray-500' : 'text-left text-gray-500'
                          }`}>
                            {message.timestamp.toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start animate-fade-in">
                      <div className="flex gap-3 max-w-[85%]">
                        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                          <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                          <div className="flex items-center gap-1">
                            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 bg-white px-4 py-4">
                <div className="flex items-end gap-3">
                  <div className="flex-1">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message here..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all bg-gray-50 hover:bg-white"
                      rows="2"
                      disabled={isLoading}
                    />
                  </div>
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Press <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-xs">Enter</kbd> to send • <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-xs">Shift + Enter</kbd> for new line
                </p>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              {/* Quick Info Card */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-200/50 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-bold text-gray-900">Features</h3>
                </div>
                <ul className="space-y-3 text-sm text-gray-700">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">✓</span>
                    <span>Instant answers to your questions</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">✓</span>
                    <span>Product information & recommendations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">✓</span>
                    <span>24/7 availability</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600 mt-0.5">✓</span>
                    <span>Bilingual support (English & Sinhala)</span>
                  </li>
                </ul>
              </div>

              {/* About Card (Expandable) */}
              {showInfo && (
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-lg border border-blue-200/50 p-6 animate-fade-in-up">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                        <Info className="w-5 h-5 text-white" />
                      </div>
                      <h3 className="font-bold text-gray-900">About This Bot</h3>
                    </div>
                    <button
                      onClick={() => setShowInfo(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="space-y-3 text-sm text-gray-700">
                    <p className="leading-relaxed">
                      This chatbot is powered by <strong className="text-blue-600">SinLlama</strong>, an advanced AI model running on Modal infrastructure.
                    </p>
                    <p className="leading-relaxed">
                      It's trained on your business's specific data including FAQs, products, and policies to provide accurate, contextual responses.
                    </p>
                    <div className="pt-3 border-t border-blue-200">
                      <p className="text-xs text-gray-600">
                        <strong>Technology:</strong> RAG-based AI • Modal Serverless • SinLlama Model
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Suggested Questions */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-200/50 p-6">
                <h3 className="font-bold text-gray-900 mb-4">Try asking...</h3>
                <div className="space-y-2">
                  {[
                    "What products do you offer?",
                    "What are your business hours?",
                    "How can I contact support?",
                    "Tell me about pricing"
                  ].map((question, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputMessage(question)}
                      className="w-full text-left px-4 py-2.5 bg-gradient-to-r from-gray-50 to-blue-50 hover:from-blue-50 hover:to-indigo-50 rounded-lg text-sm text-gray-700 hover:text-blue-700 transition-all border border-gray-200 hover:border-blue-300 hover:shadow-md"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
