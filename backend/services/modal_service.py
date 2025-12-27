"""
Modal Service Client - Handles communication with Modal RAG Service
Replaces Ollama service with Modal-based LLM inference
"""
import os
import requests
import hashlib


class ModalService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModalService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        # Modal API endpoints (will be set after deployment)
        # Use optimized serverless endpoints
        self.embedding_url = os.getenv('MODAL_EMBEDDING_URL', '')
        self.chat_url = os.getenv('MODAL_CHAT_URL', '')
        
        # Flag to track if service URLs are configured
        self.is_configured = bool(self.embedding_url and self.chat_url)
        
        self.initialized = True
        
        # Log initialization status
        if self.is_configured:
            print("✅ Modal service configured with serverless endpoints")
        else:
            print("⚠️  Modal service not configured - will use fallback methods")

    def generate_embedding(self, text):
        """
        Generate embedding using Modal serverless service with fallback
        
        Args:
            text: Text to embed
            
        Returns:
            dict: Response with success status and embedding
        """
        # If Modal not configured, use fallback immediately
        if not self.is_configured:
            print("🔄 Modal not configured, using fallback embedding")
            embedding = self._get_fallback_embedding(text)
            return {
                'success': True,
                'embedding': embedding,
                'message': 'Using fallback embedding'
            }
            
        try:
            print(f"🚀 Activating Modal serverless embedding for: {text[:50]}...")
            response = requests.post(
                self.embedding_url,  # Direct endpoint, no /embed suffix
                json={"text": text},
                timeout=30  # Increased timeout for cold starts
            )
            response.raise_for_status()
            result = response.json()
            print("✅ Modal embedding completed successfully")
            return {
                'success': True,
                'embedding': result.get('embedding'),
                'message': 'Modal embedding successful'
            }
        except Exception as e:
            print(f"❌ Modal embedding failed, using fallback: {e}")
            embedding = self._get_fallback_embedding(text)
            return {
                'success': True,
                'embedding': embedding,
                'message': f'Fallback used due to: {str(e)}'
            }

    def generate_embeddings_batch(self, texts):
        """
        Generate embeddings for multiple texts using serverless Modal
        
        Args:
            texts: List of texts to embed
            
        Returns:
            list: List of embedding vectors
        """
        if not self.is_configured:
            print("🔄 Modal not configured, using fallback embeddings")
            return [self._get_fallback_embedding(text) for text in texts]
        
        try:
            print(f"🚀 Activating Modal serverless batch embedding for {len(texts)} texts...")
            response = requests.post(
                self.embedding_url,  # Direct endpoint
                json={"texts": texts},
                timeout=120  # Longer timeout for batch processing
            )
            response.raise_for_status()
            result = response.json()
            print("✅ Modal batch embedding completed successfully")
            return result.get('embeddings')
        except Exception as e:
            print(f"❌ Error generating embeddings, using fallback: {str(e)}")
            return [self._get_fallback_embedding(text) for text in texts]

    def add_documents(self, service_id, chunks, metadata=None):
        """
        Add document chunks to vector database
        
        Args:
            service_id: Service identifier
            chunks: List of text chunks
            metadata: Optional metadata for chunks
            
        Returns:
            int: Number of chunks added
        """
        if not chunks:
            return 0
            
        collection = self.get_or_create_collection(service_id)
        
        # Generate embeddings for all chunks
        embeddings = self.generate_embeddings_batch(chunks)
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        embeddings_list = []
        metadatas = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique ID
            chunk_id = hashlib.md5(
                f"{service_id}_{chunk}_{i}".encode()
            ).hexdigest()
            
            ids.append(chunk_id)
            documents.append(chunk)
            embeddings_list.append(embedding)
            
            # Add metadata
            meta = metadata.copy() if metadata else {}
            meta['chunk_index'] = i
            meta['service_id'] = service_id
            metadatas.append(meta)
        
        # Add to ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings_list,
            documents=documents,
            metadatas=metadatas
        )
        
        return len(chunks)

    def search_documents(self, service_id, query, n_results=5):
        """
        Search for relevant documents using semantic similarity
        
        Args:
            service_id: Service identifier
            query: Search query
            n_results: Number of results to return
            
        Returns:
            dict: Search results with documents, distances, and metadata
        """
        try:
            collection = self.get_or_create_collection(service_id)
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search in ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = {
                'documents': results['documents'][0] if results['documents'] else [],
                'distances': results['distances'][0] if results['distances'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return {'documents': [], 'distances': [], 'metadatas': []}

    def generate_chat_response(
        self,
        query,
        context,
        conversation_history=None,
        language='en',
        max_tokens=256,  # Reduced default for faster response
        temperature=0.7
    ):
        """
        Generate chat response using Modal serverless service with fallback
        
        Args:
            query: User's question
            context: Retrieved relevant context
            conversation_history: Previous messages
            language: 'en', 'si', or 'mixed'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            str: Generated response
        """
        # If Modal not configured, use fallback immediately
        if not self.is_configured:
            print("🔄 Modal not configured, using fallback response")
            return self._get_fallback_response(query, context, language)
            
        try:
            print(f"🚀 Activating Modal serverless chat for query: {query[:50]}...")
            response = requests.post(
                self.chat_url,  # Direct endpoint
                json={
                    "query": query,
                    "context": context,
                    "conversation_history": conversation_history,
                    "language": language,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=120  # Increased to 120s for cold start + model loading + generation
            )
            response.raise_for_status()
            result = response.json()
            chat_response = result.get('response', '')
            print("✅ Modal chat response generated successfully")
            return chat_response
        except Exception as e:
            print(f"❌ Modal chat failed, using fallback: {e}")
            return self._get_fallback_response(query, context, language)

    def delete_collection(self, service_id):
        """Delete all data for a service"""
        # Note: This should be handled by the vector service that manages ChromaDB
        print(f"Collection deletion for service {service_id} should be handled by VectorDatabaseService")
        return True
        return True

    def detect_language(self, text):
        """
        Detect language in text (Sinhala, English, or mixed)
        
        Args:
            text: Input text
            
        Returns:
            str: 'si', 'en', or 'mixed'
        """
        # Check for Sinhala Unicode characters (U+0D80 to U+0DFF)
        has_sinhala = any('\u0D80' <= char <= '\u0DFF' for char in text)
        # Check for English characters
        has_english = any('a' <= char.lower() <= 'z' for char in text)
        
        if has_sinhala and has_english:
            return 'mixed'
        elif has_sinhala:
            return 'si'
        else:
            return 'en'

    def detect_intent(self, query):
        """
        Detect user intent from query
        
        Args:
            query: User query text
            
        Returns:
            tuple: (intent, confidence)
        """
        query_lower = query.lower()
        
        # Intent patterns with keywords
        intents = {
            'product_inquiry': ['product', 'item', 'sell', 'buy', 'price', 'cost', 'available', 'stock', 'purchase'],
            'order_tracking': ['order', 'delivery', 'track', 'shipping', 'status', 'when', 'arrive'],
            'faq': ['how', 'what', 'why', 'where', 'can i', 'do you', 'is there'],
            'complaint': ['problem', 'issue', 'wrong', 'defect', 'broken', 'complaint', 'refund', 'return'],
            'human_request': ['speak', 'talk', 'human', 'agent', 'representative', 'person'],
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'thanks': ['thank', 'thanks', 'appreciate', 'grateful']
        }
        
        # Calculate match scores
        scores = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return 'general', 0.5
        
        # Get intent with highest score
        detected_intent = max(scores, key=scores.get)
        max_score = scores[detected_intent]
        
        # Calculate confidence (normalize to 0-1)
        confidence = min(max_score / 3.0, 1.0)
        
        return detected_intent, confidence

    def check_service_available(self):
        """Check if Modal serverless service is available"""
        if not self.is_configured:
            return {
                'status': 'not_configured',
                'message': 'Modal URLs not configured. Please set MODAL_EMBEDDING_URL and MODAL_CHAT_URL in environment variables.',
                'mode': 'fallback'
            }
        
        try:
            print("🔍 Checking Modal serverless service status...")
            # Test embedding endpoint
            response = requests.post(
                self.embedding_url,  # Direct endpoint
                json={"text": "test"},
                timeout=30  # Allow time for cold start
            )
            response.raise_for_status()
            
            print("✅ Modal serverless service is operational")
            return {
                'status': 'operational',
                'message': 'Modal serverless RAG service is available',
                'mode': 'serverless'
            }
        except Exception as e:
            print(f"❌ Modal service check failed: {e}")
            return {
                'status': 'error',
                'message': f'Modal serverless service unavailable: {str(e)}',
                'mode': 'fallback'
            }
    
    def _get_fallback_embedding(self, text):
        """
        Generate simple hash-based embedding for fallback
        Returns a fixed-size vector based on text content
        """
        import hashlib
        import numpy as np
        
        # Create hash and convert to embedding vector
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 384-dimensional vector (common embedding size)
        embedding_size = 384
        embedding = []
        
        for i in range(embedding_size):
            byte_index = i % len(hash_bytes)
            value = hash_bytes[byte_index] / 255.0  # Normalize to 0-1
            embedding.append(value)
        
        return embedding
    
    def _get_fallback_response(self, query, context, language='en'):
        """
        Generate simple rule-based response for fallback
        Uses basic patterns and context information
        """
        query_lower = query.lower()
        
        # Extract keywords from context
        context_keywords = []
        if context and isinstance(context, str):
            words = context.lower().split()
            context_keywords = [word for word in words if len(word) > 3][:10]
        
        # Basic response templates
        if language == 'si' or 'sinhala' in query_lower:
            # Sinhala responses
            if any(word in query_lower for word in ['ආයුබෝවන්', 'හෙලෝ', 'hi', 'hello']):
                return "ආයුබෝවන්! මම ඔබට උදව් කිරීමට සූදානම්. ඔබගේ ප්‍රශ්නය කුමක්ද?"
            elif any(word in query_lower for word in ['ස්තූතියි', 'thanks', 'thank']):
                return "ඔබට ස්තූතියි! වෙනත් කිසිදු ප්‍රශ්නයක් තිබේද?"
            elif context_keywords:
                keywords = ', '.join(context_keywords[:3])
                return f"ඔබගේ ප්‍රශ්නය සම්බන්ධයෙන් මට තොරතුරු සොයා ගත හැකිය: {keywords}. කරුණාකර වැඩි විස්තර ලබා දෙන්න."
            else:
                return "කරුණාකර ඔබගේ ප්‍රශ්නය වැඩි පැහැදිලිව පැවසෙන්න. මම ඔබට උදව් කිරීමට උත්සාහ කරමි."
        else:
            # English responses
            if any(word in query_lower for word in ['hello', 'hi', 'hey']):
                return "Hello! I'm here to help you. What can I assist you with today?"
            elif any(word in query_lower for word in ['thanks', 'thank you']):
                return "You're welcome! Is there anything else I can help you with?"
            elif context_keywords:
                keywords = ', '.join(context_keywords[:3])
                return f"Based on the information I found about {keywords}, I can help you with your question. Could you provide more specific details?"
            else:
                return "I understand you have a question. While I'm working on getting you the best answer, could you please provide more details about what you're looking for?"


# Global instance for easy access
_modal_service_instance = None

def get_modal_service():
    """Get the global ModalService instance"""
    global _modal_service_instance
    if _modal_service_instance is None:
        _modal_service_instance = ModalService()
    return _modal_service_instance
