"""
Modal RAG Service for MarketMatic Chatbot
Provides embeddings and chat completions using Sentence Transformers and Qwen models
"""
import modal

# Create Modal app
app = modal.App("marketmatic-rag")

# Define container image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "sentence-transformers==2.7.0",
        "transformers>=4.45.0",
        "torch>=2.0.0",
        "accelerate>=0.20.0",
        "fastapi[standard]",
    )
)

# Model configuration - Using smaller, faster models for better performance
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast, 384-dim embeddings
CHAT_MODEL = "microsoft/DialoGPT-medium"  # Smaller conversational model for faster responses


@app.cls(
    image=image,
    gpu="A10",  # A10 GPU for optimal performance
    memory=64 * 1024,  # 64GB RAM for large model handling
    cpu=8,  # 8 CPU cores for parallel processing
    timeout=60,  # Standard timeout for faster models
)
class RAGService:
    @modal.enter()
    def load_models(self):
        """Load models when container starts"""
        from sentence_transformers import SentenceTransformer
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        print("Loading chat model...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            CHAT_MODEL,
            trust_remote_code=True
        )
        self.chat_model = AutoModelForCausalLM.from_pretrained(
            CHAT_MODEL,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        print("Models loaded successfully!")
    
    @modal.method()
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    @modal.method()
    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(
            texts, 
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings.tolist()
    
    @modal.method()
    def generate_chat_response(
        self,
        query: str,
        context: str,
        conversation_history: list[dict] = None,
        language: str = "en",
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> str:
        """
        Generate chat response using RAG context with a simpler, faster approach
        
        Args:
            query: User's question
            context: Retrieved relevant context from documents
            conversation_history: Previous messages (simplified for faster processing)
            language: 'en' for English, 'si' for Sinhala, 'mixed' for both
            max_tokens: Maximum tokens to generate (reduced for speed)
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        import torch
        
        # Create a simple, focused prompt for better performance
        if language == "si":
            prompt_template = """ව්‍යාපාරික සහායකයා: {context}

ප්‍රශ්නය: {query}
පිළිතුර:"""
        else:
            prompt_template = """Business Assistant Context: {context}

Customer Question: {query}
Helpful Response:"""
        
        # Format the prompt
        prompt = prompt_template.format(context=context[:500], query=query)  # Limit context for speed
        
        # Tokenize with length limits for faster processing
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,  # Reduced for faster processing
            padding=True
        ).to(self.chat_model.device)
        
        # Generate response with optimized settings for speed
        with torch.no_grad():
            outputs = self.chat_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                early_stopping=True  # Stop early for faster response
            )
        
        # Decode response
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        # Clean and format response
        response = response.strip()
        
        # Add fallback responses if model output is poor
        if not response or len(response) < 10:
            if language == "si":
                response = "මට ඔබට උදව් කිරීමට සතුටුයි. කරුණාකර වඩා විස්තරාත්මක ප්‍රශ්නයක් අසන්න."
            else:
                response = "I'm here to help! Could you please ask a more specific question about our products or services?"
        
        return response


# Web endpoints for easy HTTP access
@app.function(
    image=image,
    gpu="T4",
    memory=16 * 1024,
    cpu=4,
    timeout=60
)
@modal.fastapi_endpoint(method="POST", docs=True)
def embed(request: dict):
    """
    HTTP endpoint for generating embeddings
    
    Request body:
    {
        "text": "single text to embed"  OR  "texts": ["text1", "text2", ...]
    }
    
    Returns:
    {
        "embedding": [float, ...] OR "embeddings": [[float, ...], ...]
    }
    """
    service = RAGService()
    
    if "text" in request:
        embedding = service.generate_embedding.remote(request["text"])
        return {"embedding": embedding}
    elif "texts" in request:
        embeddings = service.generate_embeddings_batch.remote(request["texts"])
        return {"embeddings": embeddings}
    else:
        return {"error": "Must provide 'text' or 'texts' in request body"}, 400


@app.function(
    image=image,
    gpu="T4",
    memory=16 * 1024,
    cpu=4,
    timeout=60
)
@modal.fastapi_endpoint(method="POST", docs=True)
def chat(request: dict):
    """
    HTTP endpoint for generating chat responses
    
    Request body:
    {
        "query": "user question",
        "context": "relevant retrieved context",
        "conversation_history": [{"role": "user", "content": "..."}, ...] (optional),
        "language": "en" | "si" | "mixed" (optional, default "en"),
        "max_tokens": 512 (optional),
        "temperature": 0.7 (optional)
    }
    
    Returns:
    {
        "response": "generated response text"
    }
    """
    service = RAGService()
    
    # Validate required fields
    if "query" not in request or "context" not in request:
        return {"error": "Must provide 'query' and 'context' in request body"}, 400
    
    response = service.generate_chat_response.remote(
        query=request["query"],
        context=request["context"],
        conversation_history=request.get("conversation_history"),
        language=request.get("language", "en"),
        max_tokens=request.get("max_tokens", 512),
        temperature=request.get("temperature", 0.7)
    )
    
    return {"response": response}


# CLI for testing
@app.local_entrypoint()
def main(test_type: str = "embedding"):
    """
    Test the Modal RAG service
    
    Usage:
        modal run modal_rag_service.py --test-type embedding
        modal run modal_rag_service.py --test-type chat
    """
    service = RAGService()
    
    if test_type == "embedding":
        print("\n=== Testing Embedding Generation ===")
        text = "Hello, how can I help you today?"
        embedding = service.generate_embedding.remote(text)
        print(f"Text: {text}")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
    elif test_type == "chat":
        print("\n=== Testing Chat Response ===")
        query = "What products do you sell?"
        context = """
        Our shop sells:
        - T-shirts: Rs. 1500
        - Jeans: Rs. 3500
        - Shoes: Rs. 4500
        - Bags: Rs. 2000
        
        We accept cash and card payments.
        Delivery available within Colombo.
        """
        response = service.generate_chat_response.remote(
            query=query,
            context=context,
            language="en"
        )
        print(f"Query: {query}")
        print(f"\nContext: {context}")
        print(f"\nResponse: {response}")
    
    else:
        print("Invalid test_type. Use 'embedding' or 'chat'")
