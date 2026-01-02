"""
Ollama Service - Local LLM inference using Ollama
Much faster than Modal for local development
"""
import requests
import json


class OllamaService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OllamaService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.base_url = "http://localhost:11434"
        self.embedding_model = "nomic-embed-text"
        self.chat_model = "llama3"
        
        self.initialized = True
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                print("✅ Ollama service connected successfully")
                models = response.json().get('models', [])
                print(f"📦 Available models: {[m['name'] for m in models]}")
            else:
                print("⚠️  Ollama is running but returned unexpected response")
        except Exception as e:
            print(f"⚠️  Ollama connection failed: {e}")
            print("   Make sure Ollama is running: ollama serve")

    def test_connection(self):
        """Test if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate_embedding(self, text):
        """
        Generate embedding using Ollama's nomic-embed-text model
        
        Args:
            text: Text to embed
            
        Returns:
            list: Embedding vector
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get('embedding', [])
        except Exception as e:
            print(f"❌ Ollama embedding failed: {e}")
            # Return empty embedding as fallback
            return [0.0] * 768  # nomic-embed-text is 768 dimensions

    def generate_embeddings_batch(self, texts):
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            list: List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings

    def generate_chat_response(
        self,
        query,
        context,
        conversation_history=None,
        language='en',
        max_tokens=300,
        temperature=0.7
    ):
        """
        Generate chat response using Ollama's Llama3 model
        
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
        try:
            # Build conversation context
            conversation_text = ""
            if conversation_history:
                for msg in conversation_history[-3:]:  # Last 3 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    conversation_text += f"{role}: {content}\n"
            
            # Detect if Sinhala is in query
            has_sinhala = any('\u0D80' <= char <= '\u0DFF' for char in query)
            
            # Create system prompt
            if has_sinhala or language == 'si':
                system_prompt = f"""You are a helpful business assistant. Answer in both English and Sinhala as needed.

Business Information:
{context[:800]}

Previous conversation:
{conversation_text}

Instructions:
- Use the business information above to answer accurately
- Support both English and Sinhala languages
- Be concise and helpful
- If you don't know something, say so politely"""
            else:
                system_prompt = f"""You are a helpful business assistant. Answer based on the provided information.

Business Information:
{context[:800]}

Previous conversation:
{conversation_text}

Instructions:
- Use only the business information provided
- Be concise, accurate, and helpful
- If the information isn't available, politely say you don't know"""
            
            # Create messages for Llama3
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Call Ollama API with increased timeout
            print(f"🦙 Activating Ollama Llama3 for query: {query[:50]}...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.chat_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_ctx": 2048  # Context window
                    }
                },
                timeout=180  # Increased to 3 minutes for complex queries
            )
            response.raise_for_status()
            
            result = response.json()
            chat_response = result.get('message', {}).get('content', '')
            
            print("✅ Ollama chat response generated successfully")
            return chat_response.strip()
            
        except Exception as e:
            print(f"❌ Ollama chat failed: {e}")
            # Fallback response
            if has_sinhala:
                return "මට ඔබට උදව් කිරීමට කැමතියි. කරුණාකර නැවත උත්සාහ කරන්න."
            return "I'm here to help! Please try asking your question again."

    def check_service_available(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def add_documents(self, service_id, chunks, metadata=None):
        """
        Add document chunks to vector database using Ollama embeddings
        
        Args:
            service_id: Service identifier
            chunks: List of text chunks
            metadata: Optional metadata for chunks
            
        Returns:
            int: Number of chunks added
        """
        try:
            import chromadb
            import hashlib
            
            # Initialize ChromaDB client
            client = chromadb.PersistentClient(path="./data/chromadb")
            collection = client.get_or_create_collection(
                name=f"service_{service_id}",
                metadata={"service_id": service_id}
            )
            
            if not chunks:
                return 0
            
            # Generate embeddings using Ollama
            embeddings = self.generate_embeddings_batch(chunks)
            
            # Prepare data
            ids = []
            documents = []
            embeddings_list = []
            metadatas = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = hashlib.md5(
                    f"{service_id}_{chunk}_{i}".encode()
                ).hexdigest()
                
                ids.append(chunk_id)
                documents.append(chunk)
                embeddings_list.append(embedding)
                
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
            
            print(f"✅ Added {len(chunks)} chunks to vector DB using Ollama")
            return len(chunks)
            
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
            return 0

    def search_similar_documents(self, query, service_id, k=3):
        """
        Search for similar documents in vector database
        
        Args:
            query: Search query
            service_id: Service identifier
            k: Number of results to return
            
        Returns:
            list: List of relevant documents with metadata
        """
        try:
            import chromadb
            
            # Initialize ChromaDB client
            client = chromadb.PersistentClient(path="./data/chromadb")
            collection = client.get_or_create_collection(
                name=f"service_{service_id}",
                metadata={"service_id": service_id}
            )
            
            # Generate query embedding using Ollama
            query_embedding = self.generate_embedding(query)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            # Format results
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            print(f"✅ Found {len(documents)} relevant documents using Ollama")
            return documents
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []


# Global instance
_ollama_service_instance = None

def get_ollama_service():
    """Get the global OllamaService instance"""
    global _ollama_service_instance
    if _ollama_service_instance is None:
        _ollama_service_instance = OllamaService()
    return _ollama_service_instance
