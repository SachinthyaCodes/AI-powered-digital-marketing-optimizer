import React, { useState } from 'react';
import { ShoppingBag, Star, MessageCircle, X, Send, Phone, Mail, MapPin, Clock, TrendingUp, Users, Award } from 'lucide-react';

const SMEHomePage = () => {
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [welcomeLoaded, setWelcomeLoaded] = useState(false);

  // Demo service token - in production this would come from authentication
  const SERVICE_TOKEN = "demo_freshmart_token_2025";
  const API_BASE = "http://127.0.0.1:5000/api/rag";

  // Load welcome message when chat opens (simplified)
  const loadWelcomeMessage = async () => {
    if (welcomeLoaded) return;
    
    setIsLoading(true);
    
    // Simple welcome message without backend call
    const welcomeMsg = {
      id: 1,
      text: "Welcome to FreshMart! 🛒 I'm your AI shopping assistant powered by SinLlama. Ask me anything about our fresh groceries, prices, delivery, or how to place an order! (ෆ්‍රෙෂ්මාර්ට් වෙත සාදරයෙන් පිළිගන්නවා! 🛒)",
      sender: 'bot',
      time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric' }),
      language: 'mixed',
      model: 'SinLlama'
    };
    
    setMessages([welcomeMsg]);
    setWelcomeLoaded(true);
    setIsLoading(false);
  };

  // Connect to SinLlama Modal service (PEFT version)
  const sendMessageToSinLlama = async (message) => {
    try {
      const MODAL_ENDPOINT = "https://sanudasandipa29--sinllama-proper-chat-endpoint.modal.run";
      
      // Add context about FreshMart business
      const context = "You are a helpful assistant for FreshMart, a grocery delivery service in Sri Lanka. FreshMart sells fresh vegetables, fruits, and groceries with free delivery on orders above Rs. 2,000. We operate in Colombo area with 2-3 hour delivery times. Respond in a helpful, friendly manner and can use both English and Sinhala when appropriate.";
      
      const response = await fetch(MODAL_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          context: context,
          max_tokens: 150,  // Reduced to get more concise responses
          temperature: 0.7
        })
      });

      if (response.ok) {
        const data = await response.json();
        return {
          text: data.response || "I'm sorry, I couldn't generate a response. (සමාවෙන්න, මට පිළිතුරක් ජනනය කළ නොහැකි විය.)",
          language: 'mixed',
          intent: 'general',
          model: data.model || 'SinLlama_PEFT',
          contextSources: 1
        };
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Error connecting to SinLlama:', error);
      return {
        text: "I apologize, but I'm having trouble connecting to my language model right now. Please try again in a moment! (සමාවෙන්න, දැන් මගේ භාෂා ආකෘතියට සම්බන්ධ වීමට මට ගැටලුවක් තිබේ. කරුණාකර මොහොතකින් නැවත උත්සාහ කරන්න!)",
        language: 'mixed',
        error: true,
        model: 'SinLlama_PEFT (Offline)'
      };
    }
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isTyping) return;

    // Add user message
    const userMsg = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric' })
    };
    
    const currentInput = inputMessage;
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    // Get AI response from SinLlama model
    const aiResponse = await sendMessageToSinLlama(currentInput);
    
    const botMsg = {
      id: messages.length + 2,
      text: aiResponse.text,
      sender: 'bot',
      time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric' }),
      language: aiResponse.language,
      intent: aiResponse.intent,
      model: aiResponse.model,
      contextSources: aiResponse.contextSources,
      isError: aiResponse.error || false
    };
    
    setMessages(prev => [...prev, botMsg]);
    setIsTyping(false);
  };

  // Handle quick replies
  const handleQuickReply = (replyText) => {
    setInputMessage(replyText);
  };

  // Open chat and load welcome message
  const openChat = () => {
    setChatOpen(true);
    if (!welcomeLoaded) {
      loadWelcomeMessage();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Sample products
  const products = [
    { id: 1, name: 'Fresh Apples', price: 450, image: '🍎', rating: 4.5, stock: 'In Stock' },
    { id: 2, name: 'Organic Bananas', price: 280, image: '🍌', rating: 4.8, stock: 'In Stock' },
    { id: 3, name: 'Fresh Carrots', price: 120, image: '🥕', rating: 4.3, stock: 'In Stock' },
    { id: 4, name: 'Tomatoes', price: 200, image: '🍅', rating: 4.6, stock: 'Limited' },
    { id: 5, name: 'Fresh Milk', price: 350, image: '🥛', rating: 4.9, stock: 'In Stock' },
    { id: 6, name: 'Free Range Eggs', price: 580, image: '🥚', rating: 4.7, stock: 'In Stock' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <ShoppingBag className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-gray-900">FreshMart</h1>
                <p className="text-xs text-gray-500 hidden sm:block">Fresh & Organic Groceries</p>
              </div>
            </div>
            <nav className="flex items-center gap-3 sm:gap-6">
              <a href="#products" className="text-sm sm:text-base text-gray-700 hover:text-green-600">Products</a>
              <a href="#about" className="text-sm sm:text-base text-gray-700 hover:text-green-600 hidden sm:block">About</a>
              <a href="#contact" className="text-sm sm:text-base text-gray-700 hover:text-green-600">Contact</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-green-600 to-green-700 text-white py-12 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6">
              Fresh & Organic Groceries Delivered to Your Door
            </h2>
            <p className="text-lg sm:text-xl mb-6 sm:mb-8 text-green-50">
              Quality products at affordable prices. Free delivery on orders above Rs. 2,000!
            </p>
            <button className="bg-white text-green-600 px-6 sm:px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors text-sm sm:text-base">
              Shop Now
            </button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-8 sm:py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-full mb-2 sm:mb-3">
                <Users className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-gray-900">5,000+</div>
              <div className="text-xs sm:text-sm text-gray-600">Happy Customers</div>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-full mb-2 sm:mb-3">
                <ShoppingBag className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-gray-900">200+</div>
              <div className="text-xs sm:text-sm text-gray-600">Products</div>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 rounded-full mb-2 sm:mb-3">
                <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-gray-900">98%</div>
              <div className="text-xs sm:text-sm text-gray-600">Satisfaction</div>
            </div>
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-orange-100 rounded-full mb-2 sm:mb-3">
                <Award className="w-5 h-5 sm:w-6 sm:h-6 text-orange-600" />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-gray-900">10+</div>
              <div className="text-xs sm:text-sm text-gray-600">Years</div>
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section id="products" className="py-12 sm:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-6 sm:mb-8">Featured Products</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 sm:gap-6">
            {products.map((product) => (
              <div key={product.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-3 sm:p-4 border border-gray-200">
                <div className="text-5xl sm:text-6xl mb-2 sm:mb-3 text-center">{product.image}</div>
                <h3 className="font-semibold text-gray-900 mb-1 sm:mb-2 text-sm sm:text-base">{product.name}</h3>
                <div className="flex items-center gap-1 mb-2">
                  <Star className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-400 fill-current" />
                  <span className="text-xs sm:text-sm text-gray-600">{product.rating}</span>
                </div>
                <div className="flex items-center justify-between mb-2 sm:mb-3">
                  <span className="text-base sm:text-lg font-bold text-green-600">Rs. {product.price}</span>
                  <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">{product.stock}</span>
                </div>
                <button className="w-full bg-green-600 text-white py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium hover:bg-green-700 transition-colors">
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-12 sm:py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-12">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4 sm:mb-6">Get In Touch</h2>
              <p className="text-gray-600 mb-6 sm:mb-8 text-sm sm:text-base">
                Have questions? We're here to help! Contact us through any of the following methods.
              </p>
              <div className="space-y-4 sm:space-y-6">
                <div className="flex items-start gap-3 sm:gap-4">
                  <Phone className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-gray-900 text-sm sm:text-base">Phone</div>
                    <div className="text-gray-600 text-sm sm:text-base">+94 77 123 4567</div>
                  </div>
                </div>
                <div className="flex items-start gap-3 sm:gap-4">
                  <Mail className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-gray-900 text-sm sm:text-base">Email</div>
                    <div className="text-gray-600 text-sm sm:text-base">contact@freshmart.lk</div>
                  </div>
                </div>
                <div className="flex items-start gap-3 sm:gap-4">
                  <MapPin className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-gray-900 text-sm sm:text-base">Address</div>
                    <div className="text-gray-600 text-sm sm:text-base">123 Main Street, Colombo 07, Sri Lanka</div>
                  </div>
                </div>
                <div className="flex items-start gap-3 sm:gap-4">
                  <Clock className="w-5 h-5 sm:w-6 sm:h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <div className="font-semibold text-gray-900 text-sm sm:text-base">Business Hours</div>
                    <div className="text-gray-600 text-sm sm:text-base">Mon - Sat: 8:00 AM - 8:00 PM</div>
                    <div className="text-gray-600 text-sm sm:text-base">Closed on Sundays</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-green-50 p-6 sm:p-8 rounded-xl">
              <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">Send us a message</h3>
              <form className="space-y-4">
                <input
                  type="text"
                  placeholder="Your Name"
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm sm:text-base"
                />
                <input
                  type="email"
                  placeholder="Your Email"
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm sm:text-base"
                />
                <textarea
                  placeholder="Your Message"
                  rows="4"
                  className="w-full px-4 py-2.5 sm:py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm sm:text-base"
                ></textarea>
                <button className="w-full bg-green-600 text-white py-2.5 sm:py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors text-sm sm:text-base">
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 sm:py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <ShoppingBag className="w-6 h-6 sm:w-8 sm:h-8" />
              <span className="text-xl sm:text-2xl font-bold">FreshMart</span>
            </div>
            <p className="text-gray-400 text-sm sm:text-base">© 2025 FreshMart. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Chatbot Widget */}
      {!chatOpen && (
        <button
          onClick={openChat}
          className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-br from-green-500 to-green-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center z-50 hover:scale-110"
        >
          <MessageCircle className="w-6 h-6 sm:w-7 sm:h-7" />
          <span className="absolute -top-1 -right-1 w-4 h-4 sm:w-5 sm:h-5 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold animate-pulse">
            AI
          </span>
        </button>
      )}

      {/* Chatbot Window */}
      {chatOpen && (
        <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 w-[calc(100vw-2rem)] sm:w-96 h-[32rem] bg-white rounded-2xl shadow-2xl z-50 flex flex-col border border-gray-200 overflow-hidden">
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-3 sm:p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-bold text-sm sm:text-base">FreshMart AI Assistant</h3>
                <p className="text-xs text-green-100">
                  {isLoading ? 'Connecting...' : 'Online • SinLlama • සිංහල/English'}
                </p>
              </div>
            </div>
            <button
              onClick={() => setChatOpen(false)}
              className="hover:bg-green-700 p-2 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4 bg-gray-50">
            {isLoading && messages.length === 0 && (
              <div className="flex justify-center items-center py-8">
                <div className="text-sm text-gray-500">Loading welcome message...</div>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-3 sm:px-4 py-2 sm:py-2.5 ${
                    message.sender === 'user'
                      ? 'bg-green-600 text-white'
                      : message.isError
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <p className="text-xs sm:text-sm">{message.text}</p>
                  <div className="flex justify-between items-center mt-1">
                    <p className={`text-xs ${message.sender === 'user' ? 'text-green-100' : 'text-gray-500'}`}>
                      {message.time}
                    </p>
                    {message.sender === 'bot' && message.model && (
                      <p className="text-xs text-gray-400">
                        {message.model} • {message.language || 'auto'}
                        {message.contextSources > 0 && ` • ${message.contextSources} sources`}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-900 border border-gray-200 rounded-2xl px-4 py-2.5">
                  <div className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    <span className="text-xs text-gray-500 ml-2">SinLlama is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Replies */}
          <div className="px-3 sm:px-4 py-2 bg-white border-t border-gray-200">
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {[
                'Products (භාණ්ඩ)',
                'Prices (මිල)',
                'Delivery (බෙදාහැරීම)',
                'Store Hours (කාලය)',
                'Track Order (ඇණවුම)',
                'Fresh Items (නැවුම්)'
              ].map((reply, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickReply(reply.split(' ')[0])}
                  className="px-3 py-1.5 bg-green-50 hover:bg-green-100 border border-green-200 rounded-full text-xs font-medium text-green-700 whitespace-nowrap transition-colors"
                >
                  {reply}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Input */}
          <div className="p-3 sm:p-4 bg-white border-t border-gray-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isTyping}
                placeholder={isTyping ? "AI is thinking..." : "Ask about products, prices, delivery... (සිංහල/English)"}
                className="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 border border-gray-300 rounded-full focus:ring-2 focus:ring-green-500 focus:border-transparent text-xs sm:text-sm disabled:bg-gray-50 disabled:text-gray-400"
              />
              <button
                onClick={handleSendMessage}
                disabled={isTyping || inputMessage.trim() === ''}
                className="w-10 h-10 bg-green-600 text-white rounded-full flex items-center justify-center hover:bg-green-700 transition-colors flex-shrink-0 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>
            <div className="text-xs text-gray-500 mt-2 text-center">
              Powered by SinLlama AI • Understands සිංහල & English
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SMEHomePage;
