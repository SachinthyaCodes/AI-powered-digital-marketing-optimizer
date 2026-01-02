"""
SinLlama Service - 100% OFFLINE Local GGUF Model inference using llama-cpp-python
Supports both English and Sinhala languages with advanced prompt engineering
Optimized for smooth, user-friendly responses
Integrated with RAG system for context-aware generation
"""
import os
import re
from typing import Optional, List, Dict
from llama_cpp import Llama

class SinLlamaService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SinLlamaService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
        
        # Path to the GGUF model
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'models',
            'sinllama-q4_k_m.gguf'
        )
        
        print(f"[SinLlama] Loading model...")
        
        try:
            # Get CPU core count for optimal threading
            import multiprocessing
            cpu_cores = multiprocessing.cpu_count()
            optimal_threads = max(4, cpu_cores - 2)  # Leave 2 cores for system
            
            # Initialize the model with OPTIMIZED CPU SETTINGS
            self.llm = Llama(
                model_path=self.model_path,
                
                # Context & Memory Settings - BALANCED for CPU
                n_ctx=2048,              # Reduced context to save memory
                n_batch=256,             # Smaller batch size for memory efficiency
                use_mlock=False,         # Don't lock in RAM (saves memory)
                use_mmap=True,           # Memory-mapped file access (faster loading)
                
                # CPU Settings - OPTIMIZED for your system
                n_threads=optimal_threads,  # Use most CPU cores
                n_gpu_layers=0,          # CPU only (no GPU available)
                
                # Performance Optimizations
                f16_kv=True,             # Use FP16 for key/value cache (saves memory)
                logits_all=False,        # Only compute logits for last token (faster)
                vocab_only=False,        # Load full model
                
                # Output Control
                verbose=False            # Suppress verbose llama.cpp output
            )
            print("✅ SinLlama model loaded successfully!")
            self.initialized = True
        except Exception as e:
            print(f"❌ Failed to load SinLlama model: {e}")
            self.llm = None
            self.initialized = False
    
    def check_service_available(self) -> bool:
        """Check if the model is loaded and ready"""
        return self.llm is not None
    
    def _detect_language(self, text: str) -> str:
        """
        Detect if text contains Sinhala, English, or mixed
        Returns: 'si', 'en', or 'mixed'
        """
        has_sinhala = bool(re.search(r'[\u0D80-\u0DFF]', text))
        has_english = bool(re.search(r'[a-zA-Z]', text))
        
        if has_sinhala and has_english:
            return 'mixed'
        elif has_sinhala:
            return 'si'
        else:
            return 'en'
    
    def _clean_response(self, response: str) -> str:
        """
        Clean and polish the generated response for better user experience
        - Remove repetitive patterns
        - Fix common formatting issues
        - Ensure proper punctuation
        """
        if not response:
            return response
        
        # Remove excessive newlines
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # Remove repetitive sentences (basic deduplication)
        sentences = response.split('.')
        seen = set()
        unique_sentences = []
        for sentence in sentences:
            normalized = sentence.strip().lower()
            if normalized and normalized not in seen and len(normalized) > 10:
                seen.add(normalized)
                unique_sentences.append(sentence.strip())
        
        response = '. '.join(unique_sentences)
        if response and not response.endswith('.'):
            response += '.'
        
        # Remove phrases that indicate the model is confused
        confused_phrases = [
            "I don't have enough information in the context",
            "Based on the context provided",
            "According to the information above",
            "I apologize but I don't see"
        ]
        
        for phrase in confused_phrases:
            if phrase.lower() in response.lower():
                # Model is uncertain, provide fallback
                return self._get_fallback_response()
        
        return response.strip()
    
    def _get_fallback_response(self) -> str:
        """Get a friendly fallback response when model is uncertain"""
        return ("I'd love to help you with that! Could you please rephrase your question or ask about our "
                "plans, pricing, features, or how our service works? 😊")
    
    def generate_chat_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List] = None,
        language: str = 'mixed',
        max_tokens: int = 350,
        temperature: float = 0.75
    ) -> str:
        """
        Generate chat response using the SinLlama GGUF model with ADVANCED PROMPT ENGINEERING
        
        Args:
            query: User's question
            context: Retrieved relevant context
            conversation_history: Previous messages
            language: 'en', 'si', or 'mixed' (auto-detected)
            max_tokens: Maximum tokens to generate (increased for better responses)
            temperature: Sampling temperature (0.75 for more natural responses)
            
        Returns:
            str: Generated smooth, user-friendly response
        """
        if not self.check_service_available():
            return "⚠️ Sorry, the AI service is currently unavailable. Please try again in a moment."
        
        try:
            # Auto-detect language from user query
            detected_lang = self._detect_language(query)
            
            # Build conversation context (last 4 messages for better context)
            conversation_text = ""
            if conversation_history and len(conversation_history) > 0:
                for msg in conversation_history[-4:]:  # Last 4 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        conversation_text += f"Customer: {content}\n"
                    else:
                        conversation_text += f"You: {content}\n"
            
            # === ADVANCED PROMPT ENGINEERING FOR SMOOTH RESPONSES ===
            
            if detected_lang in ['si', 'mixed']:
                # BILINGUAL PROMPT - Natural mixing of Sinhala & English
                system_prompt = f"""You are a friendly, helpful AI assistant for a business. Your job is to answer customer questions accurately using the information provided.

📚 BUSINESS INFORMATION (Use this to answer):
{context[:4000]}

💬 CONVERSATION SO FAR:
{conversation_text}

🎯 YOUR MISSION:
Answer the customer's question naturally and helpfully. Be conversational, warm, and accurate.

⚠️ CRITICAL RULE - RELEVANCE CHECK:
BEFORE answering, ask yourself: "Does the provided information actually relate to the customer's question?"
- If YES: Answer using that information
- if NO: Say you don't have that information (see examples below)

✨ RESPONSE STYLE GUIDELINES:

1. **RELEVANCE IS EVERYTHING**:
   • ONLY answer if the provided information is RELEVANT to the question
   • If information doesn't match the question, say you don't have it
   • NEVER make up information or use irrelevant context

2. **LANGUAGE MATCHING** (Critical!):
   • If customer uses English → Reply in English
   • If customer uses Sinhala → Reply in Sinhala  
   • If customer mixes both → Mix naturally

3. **BE NATURAL & CONVERSATIONAL**:
   • Speak like a helpful friend, not a robot
   • Use emojis occasionally (😊 🎉 ✅) to be friendly
   • Keep sentences short and easy to read

4. **BE SPECIFIC & ACCURATE**:
   • Give exact prices, numbers, and details from the info above
   • Don't make up information - use ONLY what's provided
   • If information is irrelevant or not found: admit it honestly

5. **WHEN YOU DON'T KNOW** (VERY IMPORTANT):
   • English: "I don't have information about that in my knowledge base. Can I help you with something else? 😊"
   • Sinhala: "මට ඒ ගැන විස්තර මගේ database එකේ නැහැ 😊 වෙනත් දෙයක් උදව් කරන්න පුළුවන්ද?"
   • NEVER use irrelevant information to answer a different question!

📝 EXAMPLE CONVERSATIONS:

Q: "Do you have laptops?"
Context: [Information about vegetables and groceries]
A: "I don't have information about laptops 😊 My knowledge base is about groceries. Can I help you with fresh vegetables or fruits instead?"

Q: "මිල කීයද?"
Context: [Random text about unrelated topics]
A: "මට ඔබ අහන දේ ගැන මේ database එකේ විස්තර නැහැ 😊 වෙනත් දෙයක් ඇහුවොත් උදව් කරන්න පුළුවන්."

Q: "Basic plan එකේ මිල කීයද?"
Context: [Plans: Basic Rs. 2,500, Pro Rs. 5,000]
A: "Basic plan එකේ මිල monthly Rs. 2,500 යි 😊 ඒකෙන් ලැබෙන්නේ 1 AI chatbot, 100 conversations."

Q: "Do you have non-dairy milk?"
Context: [Product list including: Almond Milk Rs.350, Soy Milk Rs.300]
A: "Yes! We have non-dairy options 🎉 Almond Milk (Rs. 350) and Soy Milk (Rs. 300). Both are fresh and available!"

Now answer this customer's question (ONLY if you have RELEVANT information):"""

            else:
                # ENGLISH-ONLY PROMPT - Professional yet friendly
                system_prompt = f"""You are a friendly AI assistant for a business. Answer customer questions using the information below.

📚 BUSINESS INFORMATION:
{context[:4000]}

💬 PREVIOUS CONVERSATION:
{conversation_text}

🎯 YOUR TASK:
Answer the customer's question accurately and naturally using the business information above.

⚠️ CRITICAL RULE - RELEVANCE CHECK:
BEFORE answering, verify: "Is the provided information RELEVANT to this question?"
- If YES: Answer using that information
- If NO: Politely say you don't have that information

✨ RESPONSE RULES:

1. **RELEVANCE FIRST**: ONLY answer if you have RELEVANT information. Don't use random context!
2. **BE DIRECT**: Answer the question immediately - no fluff or long intros
3. **BE SPECIFIC**: Include exact prices, numbers, and details from the info above
4. **BE BRIEF**: 2-4 sentences maximum. Short and sweet wins!
5. **BE FRIENDLY**: Use a warm, conversational tone. Add 😊 or 🎉 occasionally
6. **BE ACCURATE**: Use ONLY information provided above. Don't make things up!
7. **BE HELPFUL**: End by offering to help with related questions

📝 PERFECT EXAMPLES:

Q: "What pricing plans do you offer?"
Context: [Plan info: Basic Rs.2500, Pro Rs.5000, Enterprise custom]
A: "We have 3 plans to choose from! 😊 Basic at Rs. 2,500/month (1 chatbot, 100 conversations), Pro at Rs. 5,000/month (3 chatbots, 1000 conversations), and Enterprise with custom pricing (unlimited chatbots). Which one interests you?"

Q: "Do you have vegan options?"
Context: [Product list with NO vegan items mentioned]
A: "I don't have information about vegan options in my current knowledge base 😊 Can I help you with other products or services we offer?"

Q: "How much is the Pro plan?"
Context: [Plans: Basic Rs.2500, Pro Rs.5000]
A: "The Pro plan is Rs. 5,000 per month 💰 You get 3 chatbots, 1000 conversations, advanced analytics, and priority support. Great for growing businesses! Want to know more about any features?"

Q: "Do you deliver to Kandy?"
Context: [Random unrelated information about products]
A: "I don't have delivery information available right now 😊 Can I help you with our products or other services instead?"

Now answer this (ONLY if you have RELEVANT information):"""
            
            # Create the full prompt
            prompt = f"""{system_prompt}

Customer: {query}
You:"""
            
            print(f"[SinLlama] 🤖 Generating smooth response ({detected_lang})...")
            
            # === OPTIMIZED GENERATION PARAMETERS FOR QUALITY ===
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,      # 0.75 = more natural, less robotic
                
                # Advanced sampling for natural language
                top_p=0.92,                   # Nucleus sampling - more diverse
                top_k=45,                     # Consider top 45 tokens
                repeat_penalty=1.18,          # Strong penalty against repetition
                frequency_penalty=0.3,        # Discourage overused tokens
                presence_penalty=0.2,         # Encourage topic diversity
                
                # Better stopping conditions
                stop=[
                    "Customer:", "\nCustomer:", 
                    "User:", "\nUser:",
                    "Human:", "\nHuman:",
                    "\n\nCustomer:", "\n\nUser:",
                    "Q:", "\nQ:"
                ],
                
                # Generation control
                echo=False,                   # Clean output
                stream=False,                 # Can enable for streaming later
                
                # Advanced parameters for coherence
                mirostat_mode=2,              # Mirostat 2.0 for better coherence
                mirostat_tau=4.5,             # Target entropy (lower = more focused)
                mirostat_eta=0.15,            # Learning rate for perplexity
            )
            
            # Extract and clean the response
            generated_text = response['choices'][0]['text'].strip()
            
            # Clean up the response for better UX
            cleaned_response = self._clean_response(generated_text)
            
            # Log metrics
            if 'usage' in response:
                tokens_used = response['usage'].get('total_tokens', 0)
                print(f"✅ Generated: {tokens_used} tokens | Lang: {detected_lang}")
            else:
                print(f"✅ Response generated | Lang: {detected_lang}")
            
            return cleaned_response if cleaned_response else self._get_fallback_response()
            
        except Exception as e:
            print(f"❌ SinLlama generation error: {e}")
            import traceback
            traceback.print_exc()
            
            # Friendly error message
            if detected_lang == 'si':
                return "මට දැන් technical issue එකක් තියෙනවා 😔 ටිකක් බලලා නැවත try කරන්න පුළුවන්ද?"
            else:
                return "I'm experiencing a technical hiccup right now 😔 Could you please try again in a moment?"
    
    def generate_simple_response(self, prompt: str, max_tokens: int = 250) -> str:
        """
        Generate a simple response without context (for quick queries)
        100% OFFLINE - No internet required
        
        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum tokens to generate
            
        Returns:
            str: Generated response
        """
        if not self.check_service_available():
            return "Sorry, the AI service is currently unavailable."
        
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=0.75,              # More natural
                top_p=0.92,
                top_k=45,
                repeat_penalty=1.18,
                frequency_penalty=0.3,
                presence_penalty=0.2,
                stop=["\n\n\n", "###"],
                echo=False,
                mirostat_mode=2,               # Better coherence
                mirostat_tau=4.5,
                mirostat_eta=0.15
            )
            
            generated = response['choices'][0]['text'].strip()
            return self._clean_response(generated) if generated else "I'm here to help! How can I assist you?"
            
        except Exception as e:
            print(f"❌ SinLlama error: {e}")
            return "I apologize, but I encountered an error."
    
    def get_service_info(self) -> Dict:
        """
        Get detailed information about the SinLlama service
        Confirms 100% OFFLINE operation
        """
        return {
            "service_name": "SinLlama Local GGUF Service",
            "status": "online" if self.check_service_available() else "offline",
            "model_path": self.model_path,
            "offline_mode": True,  # ✅ 100% OFFLINE
            "internet_required": False,  # ✅ NO INTERNET NEEDED
            "languages_supported": ["English", "Sinhala", "සිංහල", "Mixed/Bilingual"],
            "capabilities": [
                "Chat conversations",
                "Context-aware responses", 
                "RAG integration",
                "Bilingual support",
                "Offline inference"
            ],
            "optimizations": [
                "Advanced prompt engineering",
                "Response cleaning & polishing",
                "Natural language generation",
                "Mirostat 2.0 for coherence",
                "Anti-repetition mechanisms"
            ]
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # RAG INTEGRATION METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    def generate_rag_response(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        language: str = 'si'
    ) -> Dict:
        """
        Generate response using RAG-prepared prompt
        
        This method is specifically designed for RAG workflow where the
        prompt already contains retrieved context and is properly formatted.
        
        Args:
            prompt: RAG-prepared prompt with context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            language: Expected response language
        
        Returns:
            Dict with response, tokens used, and metadata
        """
        if not self.check_service_available():
            return {
                'success': False,
                'error': 'Model not available',
                'response': 'AI සේවාව දැන් ලබා ගත නොහැක.' if language == 'si' else 'AI service currently unavailable.'
            }
        
        try:
            print(f"[SinLlama RAG] 🤖 Generating response...")
            
            # Generate with RAG-optimized parameters
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                
                # RAG-specific sampling
                top_p=0.9,                    # Slightly more focused for factual answers
                top_k=40,
                repeat_penalty=1.15,
                frequency_penalty=0.2,
                presence_penalty=0.1,
                
                # Stopping conditions
                stop=[
                    "ප්‍රශ්නය:",  # Sinhala "Question:"
                    "Question:",
                    "\n\nසන්දර්භය:",  # Sinhala "Context:"
                    "\n\nContext:",
                    "User:",
                    "Customer:"
                ],
                
                echo=False,
                stream=False,
                
                # Coherence optimization
                mirostat_mode=2,
                mirostat_tau=4.0,
                mirostat_eta=0.1
            )
            
            # Extract response
            generated_text = response['choices'][0]['text'].strip()
            cleaned = self._clean_response(generated_text)
            
            # Get token usage
            usage = response.get('usage', {})
            
            print(f"✅ RAG response generated: {len(cleaned)} chars")
            
            return {
                'success': True,
                'response': cleaned,
                'tokens_used': usage.get('total_tokens', 0),
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
                'language': language
            }
            
        except Exception as e:
            print(f"❌ RAG generation error: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = 'පිළිතුර ජනනය කිරීමේදී දෝෂයක් සිදු විය.' if language == 'si' else 'Error generating response.'
            
            return {
                'success': False,
                'error': str(e),
                'response': error_msg
            }


# Create singleton instance
def get_sinllama_service():
    """Get or create SinLlama service instance"""
    return SinLlamaService()
