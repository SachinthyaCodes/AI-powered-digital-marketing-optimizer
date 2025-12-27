"""
OPTIMIZED Modal RAG Service for MarketMatic Chatbot
TRUE SERVERLESS: Only activates when API calls are made
Provides embeddings and chat completions using Sentence Transformers and Qwen models
"""
import modal

# Create Modal app
app = modal.App("marketmatic-rag-optimized")

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

# Model configuration - Using fast, lightweight models for reliability
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast, 384-dim embeddings
CHAT_MODEL = "google/flan-t5-small"  # Smaller, faster model - loads in <10 seconds


# ========== SERVERLESS FUNCTIONS (NO CLASS) ==========
# These functions only activate when called via API

@app.function(
    image=image,
    gpu="A10",
    memory=64 * 1024,  # 64GB RAM for optimal performance
    cpu=8,  # 8 CPU cores for parallel processing
    timeout=30,  # Reduced timeout for faster cleanup
    scaledown_window=60,  # Container shuts down after 1 minute of inactivity
    min_containers=0,  # No keep-warm containers to save costs
)
def generate_embedding_serverless(text: str) -> list[float]:
    """
    Generate embedding for a single text - SERVERLESS
    Container starts only when called and shuts down when idle
    """
    from sentence_transformers import SentenceTransformer
    
    # Load model on-demand (cached within container lifecycle)
    model = SentenceTransformer(EMBEDDING_MODEL)
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


@app.function(
    image=image,
    gpu="A10",
    memory=64 * 1024,
    cpu=8,
    timeout=60,  # Slightly longer for batch processing
    scaledown_window=60,
    min_containers=0,
)
def generate_embeddings_batch_serverless(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts - SERVERLESS
    More efficient for batch processing
    """
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(
        texts, 
        convert_to_numpy=True,
        show_progress_bar=False
    )
    return embeddings.tolist()


@app.function(
    image=image,
    gpu="A10",
    memory=32 * 1024,  # Reduced to 32GB for faster startup
    cpu=4,  # Reduced CPU for faster allocation
    timeout=120,  # Increased timeout for model loading
    scaledown_window=120,  # Keep warm longer
    min_containers=0
)
def generate_chat_response_serverless(
    query: str,
    context: str,
    conversation_history: list[dict] = None,
    language: str = "en",
    max_tokens: int = 256,
    temperature: float = 0.7
) -> str:
    """
    Generate chat response using RAG context - SERVERLESS
    Container only runs when chat response is needed
    Uses FLAN-T5 for instruction-following with business context
    """
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch
    
    # Load FLAN-T5 model on-demand
    tokenizer = T5Tokenizer.from_pretrained(CHAT_MODEL)
    model = T5ForConditionalGeneration.from_pretrained(
        CHAT_MODEL,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Build conversation context
    conversation_text = ""
    if conversation_history:
        for msg in conversation_history[-3:]:  # Last 3 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation_text += f"{role}: {content}\n"
    
    # Create instruction-based prompt for FLAN-T5
    if language == "si" or any('\u0D80' <= char <= '\u0DFF' for char in query):
        # Sinhala-friendly prompt
        prompt = f"""You are a helpful business assistant. Use this information to answer:

{context[:600]}

Previous conversation:
{conversation_text}

Customer question: {query}

Provide a helpful, accurate answer based on the information above. Support both English and Sinhala."""
    else:
        # English prompt
        prompt = f"""You are a helpful business assistant. Answer the customer's question using only the information provided below.

Business Information:
{context[:600]}

Previous conversation:
{conversation_text}

Customer Question: {query}

Answer:"""
    
    # Tokenize input
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(model.device)
    
    # Generate response with FLAN-T5 (optimized for speed)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=min(max_tokens, 150),  # Limit to 150 tokens max
            temperature=temperature,
            do_sample=False,  # Faster greedy decoding
            num_beams=1,  # No beam search for speed
            early_stopping=True
        )
    
    # Decode response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    # Quality check and fallback
    if not response or len(response) < 10:
        # Extract key info from context for fallback
        if 'product' in query.lower() or 'price' in query.lower():
            # Try to extract product info from context
            lines = [l.strip() for l in context.split('\n') if l.strip() and len(l.strip()) > 10]
            if lines:
                response = "Based on our information:\n\n" + "\n".join(lines[:3])
            else:
                response = "I can help you with product information. Could you be more specific about what you're looking for?"
        elif any('\u0D80' <= char <= '\u0DFF' for char in query):
            response = "මට ඔබට උදව් කිරීමට සතුටුයි. කරුණාකර වඩා විස්තරාත්මක ප්‍රශ්නයක් අසන්න."
        else:
            response = "I'm here to help! Could you please provide more details about your question?"
    
    return response


# ========== HTTP ENDPOINTS (SERVERLESS) ==========

@app.function(
    image=image,
    gpu="A10",
    memory=64 * 1024,
    cpu=8,
    timeout=90,
    scaledown_window=120,
    min_containers=0,
)
@modal.asgi_app()
def embed_api():
    """
    HTTP endpoint for generating embeddings - TRULY SERVERLESS
    Only runs when HTTP request is received
    """
    from fastapi import FastAPI, HTTPException
    
    web_app = FastAPI(title="MarketMatic Embedding API")
    
    @web_app.post("/embed")
    async def embed_text(request: dict):
        """
        Generate embeddings for text(s)
        
        Request body:
        {
            "text": "single text to embed"  OR  "texts": ["text1", "text2", ...]
        }
        """
        try:
            if "text" in request:
                embedding = generate_embedding_serverless.remote(request["text"])
                return {"embedding": embedding}
            elif "texts" in request:
                embeddings = generate_embeddings_batch_serverless.remote(request["texts"])
                return {"embeddings": embeddings}
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Must provide 'text' or 'texts' in request body"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return web_app


@app.function(
    image=image,
    gpu="A10",
    memory=32 * 1024,  # 32GB is enough for flan-t5-small
    cpu=4,
    timeout=120,  # Longer timeout to handle cold starts
    scaledown_window=120,  # Keep warm for 2 minutes
    min_containers=0
)
@modal.asgi_app()
def chat_api():
    """
    HTTP endpoint for generating chat responses - TRULY SERVERLESS
    Only runs when HTTP request is received
    """
    from fastapi import FastAPI, HTTPException
    
    web_app = FastAPI(title="MarketMatic Chat API")
    
    @web_app.post("/chat")
    async def chat_response(request: dict):
        """
        Generate chat response using RAG
        
        Request body:
        {
            "query": "user question",
            "context": "relevant retrieved context",
            "conversation_history": [{"role": "user", "content": "..."}, ...] (optional),
            "language": "en" | "si" | "mixed" (optional, default "en"),
            "max_tokens": 256 (optional),
            "temperature": 0.7 (optional)
        }
        """
        try:
            # Validate required fields
            if "query" not in request or "context" not in request:
                raise HTTPException(
                    status_code=400,
                    detail="Must provide 'query' and 'context' in request body"
                )
            
            response = generate_chat_response_serverless.remote(
                query=request["query"],
                context=request["context"],
                conversation_history=request.get("conversation_history"),
                language=request.get("language", "en"),
                max_tokens=request.get("max_tokens", 256),
                temperature=request.get("temperature", 0.7)
            )
            
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return web_app


# CLI for testing
@app.local_entrypoint()
def main(test_type: str = "embedding"):
    """
    Test the serverless Modal RAG service
    
    Usage:
        modal run modal_rag_service_optimized.py --test-type embedding
        modal run modal_rag_service_optimized.py --test-type chat
    """
    if test_type == "embedding":
        print("\n=== Testing Serverless Embedding Generation ===")
        text = "Hello, how can I help you today?"
        embedding = generate_embedding_serverless.remote(text)
        print(f"Text: {text}")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
    elif test_type == "chat":
        print("\n=== Testing Serverless Chat Response ===")
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
        response = generate_chat_response_serverless.remote(
            query=query,
            context=context,
            language="en"
        )
        print(f"Query: {query}")
        print(f"\nContext: {context}")
        print(f"\nResponse: {response}")
    
    else:
        print("Invalid test_type. Use 'embedding' or 'chat'")

# ========== STATUS CHECK FUNCTION ==========

@app.function(
    image=modal.Image.debian_slim(python_version="3.11"),
    memory=512,  # Minimal memory for status check
    cpu=1,
    timeout=10,
    scaledown_window=30,
    min_containers=0
)
def check_service_status():
    """
    Lightweight status check function
    """
    import time
    return {
        "status": "operational",
        "message": "Serverless Modal RAG service is available",
        "timestamp": time.time(),
        "mode": "serverless"
    }