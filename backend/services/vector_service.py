"""
Vector Service using Supabase pgvector
Uses SinLlama model for embeddings (NO Ollama dependency)
"""
import os
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.sqlalchemy_models import DocumentEmbedding, Document, Service
from dotenv import load_dotenv

load_dotenv()

class VectorDatabaseService:
    """Vector database service using Supabase pgvector with SinLlama embeddings"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.embedding_dim = 768  # Standard embedding dimension
        self._llm = None
        
    def _get_llm(self):
        """Lazy load SinLlama model for embeddings"""
        if self._llm is None:
            try:
                from llama_cpp import Llama
                model_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'models',
                    'sinllama-q4_k_m.gguf'
                )
                # Load model with embedding=True for embedding generation
                self._llm = Llama(
                    model_path=model_path,
                    n_ctx=512,  # Small context for embeddings
                    n_batch=64,
                    embedding=True,  # Enable embedding mode
                    verbose=False
                )
                print("✅ SinLlama embedding model loaded")
            except Exception as e:
                print(f"⚠️ Failed to load SinLlama for embeddings: {e}")
                self._llm = None
        return self._llm
    
    def generate_embedding(self, text):
        """
        Generate embedding for text using SinLlama model
        Returns: list of floats (768 dimensions)
        """
        if not text or len(text.strip()) == 0:
            print("⚠️ Empty text provided, using zero embedding")
            return [0.0] * 768
        
        try:
            llm = self._get_llm()
            if llm is not None:
                # Truncate text to reasonable length for embedding
                text_truncated = text[:512] if len(text) > 512 else text
                
                # Generate embedding using llama-cpp-python
                embedding = llm.embed(text_truncated)
                
                # Convert to list if needed
                if hasattr(embedding, 'tolist'):
                    embedding = embedding.tolist()
                elif isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                elif not isinstance(embedding, list):
                    embedding = list(embedding)
                
                # Ensure it's 768-dimensional
                if len(embedding) != 768:
                    print(f"⚠️ Embedding size {len(embedding)}, adjusting to 768")
                    # Pad or truncate to 768 dimensions
                    if len(embedding) < 768:
                        embedding = list(embedding) + [0.0] * (768 - len(embedding))
                    else:
                        embedding = embedding[:768]
                
                # Normalize the embedding for better similarity search
                norm = sum(x*x for x in embedding) ** 0.5
                if norm > 0:
                    embedding = [x/norm for x in embedding]
                
                return embedding
            else:
                print("⚠️ SinLlama model not loaded, using text-based embedding")
                return self._generate_dummy_embedding(text)
        except Exception as e:
            print(f"⚠️ Error generating embedding with SinLlama: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_dummy_embedding(text)
    
    def _generate_dummy_embedding(self, text):
        """Generate deterministic dummy embedding based on text content"""
        import hashlib
        import random
        
        # Create deterministic seed from text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16) % (2**32)
        random.seed(seed)
        
        # Generate 768-dimensional vector
        return [random.gauss(0, 0.1) for _ in range(768)]
    
    def generate_embeddings_batch(self, texts):
        """
        Generate embeddings for multiple texts
        Returns: list of embedding lists
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings
    
    def add_document_embeddings(self, document_id, service_id, chunks, db_session):
        """
        Add document embeddings to pgvector (SERVICE-SPECIFIC for multi-business support)
        Args:
            document_id: UUID of the document
            service_id: UUID of the service (ensures business isolation)
            chunks: List of text chunks
            db_session: SQLAlchemy session
        Returns:
            List of created embedding IDs
        """
        embedding_ids = []
        print(f"\n[RAG] 📚 Processing {len(chunks)} chunks for SERVICE {str(service_id)[:8]}...")
        
        # Convert UUIDs to strings for consistency
        document_id_str = str(document_id)
        service_id_str = str(service_id)
        
        try:
            for chunk_index, chunk in enumerate(chunks):
                if not chunk or len(chunk.strip()) < 10:
                    print(f"  [SKIP] Chunk {chunk_index + 1} too short, skipping...")
                    continue
                
                print(f"  [CHUNK {chunk_index + 1}/{len(chunks)}] Processing...")
                
                # Generate embedding using SinLlama
                embedding_vector = self.generate_embedding(chunk)
                
                if not embedding_vector or len(embedding_vector) != 768:
                    print(f"  [WARN] Invalid embedding for chunk {chunk_index}, regenerating...")
                    embedding_vector = self._generate_dummy_embedding(chunk)
                
                # Verify embedding is valid
                if len(embedding_vector) != 768:
                    print(f"  [ERROR] Still invalid embedding size: {len(embedding_vector)}")
                    continue
                
                print(f"  ✅ Generated embedding [{chunk[:40]}...]")
                
                # Create embedding record with BUSINESS ISOLATION
                doc_embedding = DocumentEmbedding(
                    id=str(__import__('uuid').uuid4()),
                    document_id=document_id_str,
                    service_id=service_id_str,  # Critical for multi-business support
                    chunk_index=chunk_index,
                    content=chunk,
                    embedding=embedding_vector
                )
                
                db_session.add(doc_embedding)
                embedding_ids.append(doc_embedding.id)
            
            # Commit all embeddings at once
            db_session.commit()
            print(f"\n✅ SUCCESS: {len(embedding_ids)} embeddings stored for SERVICE {service_id_str[:8]}")
            print(f"   📊 Business data is isolated and secure!\n")
            return embedding_ids
            
        except Exception as e:
            db_session.rollback()
            print(f"\n❌ ERROR adding embeddings: {e}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise to let caller handle
    
    def search_similar_documents(self, query, service_id, limit=5, db_session=None):
        """
        Search for similar documents using pgvector cosine similarity
        ⭐ BUSINESS-SPECIFIC search - only searches within the specific service's documents
        Fallback to text matching if embeddings fail
        Returns: List of similar chunks with relevance scores
        """
        if not db_session:
            print("[ERROR] No database session provided")
            return []
        
        if not query or len(query.strip()) == 0:
            print("[WARN] Empty query provided")
            return []
        
        service_id_str = str(service_id)
        print(f"\n[SEARCH] 🔍 Searching in SERVICE {service_id_str[:8]}... Query: '{query[:60]}...'")
        
        try:
            # Check if this service has any embeddings
            from models.sqlalchemy_models import DocumentEmbedding
            embedding_count = db_session.query(DocumentEmbedding).filter(
                DocumentEmbedding.service_id == service_id_str
            ).count()
            
            if embedding_count == 0:
                print(f"[INFO] No documents uploaded yet for SERVICE {service_id_str[:8]}")
                return []
            
            print(f"[INFO] Service has {embedding_count} document chunks available")
            
            # Try to generate query embedding
            query_embedding = self.generate_embedding(query)
            
            if query_embedding and len(query_embedding) == 768:
                # Use vector similarity search with cosine distance
                print("[SEARCH] ✅ Using vector similarity search (AI-powered)...")
                
                # Convert embedding to PostgreSQL array format
                embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'
                
                results = db_session.execute(text("""
                    SELECT 
                        id,
                        document_id,
                        service_id,
                        chunk_index,
                        content as chunk_text,
                        1 - (embedding <=> :query_embedding::vector) as similarity_score
                    FROM document_embeddings
                    WHERE service_id = :service_id
                    ORDER BY embedding <=> :query_embedding::vector
                    LIMIT :limit
                """), {
                    "query_embedding": embedding_str,
                    "service_id": service_id_str,
                    "limit": limit
                }).fetchall()
            else:
                # Fallback to text search
                print("[SEARCH] ⚠️ Using keyword search (fallback mode)...")
                query_words = [w.lower() for w in query.split() if len(w) > 2]
                
                if not query_words:
                    query_words = query.lower().split()
                
                # Build search with OR conditions for better matching
                search_conditions = []
                params = {"service_id": service_id_str, "limit": limit}
                
                for i, word in enumerate(query_words):
                    param_name = f"word{i}"
                    search_conditions.append(f"LOWER(content) LIKE :{param_name}")
                    params[param_name] = f"%{word}%"
                
                if search_conditions:
                    where_clause = " OR ".join(search_conditions)
                else:
                    where_clause = "1=1"
                
                results = db_session.execute(text(f"""
                    SELECT 
                        id,
                        document_id,
                        service_id,
                        chunk_index,
                        content as chunk_text,
                        0.7 as similarity_score
                    FROM document_embeddings
                    WHERE service_id = :service_id
                    AND ({where_clause})
                    LIMIT :limit
                """), params).fetchall()
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'id': str(row[0]),
                    'document_id': str(row[1]),
                    'chunk_index': row[3],
                    'chunk_text': row[4],
                    'similarity_score': float(row[5])
                })
            
            if formatted_results:
                scores_str = ', '.join([f"{r['similarity_score']:.2f}" for r in formatted_results])
                print(f"✅ Found {len(formatted_results)} relevant chunks (scores: {scores_str})")
            else:
                print("[INFO] No relevant chunks found for this query")
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error in vector search: {e}")
            import traceback
            traceback.print_exc()
            
            # Final fallback: simple ORM-based text search
            try:
                print("[SEARCH] Using final fallback: basic keyword matching...")
                from models.sqlalchemy_models import DocumentEmbedding
                query_lower = query.lower()
                query_words = [w for w in query_lower.split() if len(w) > 2]
                
                results = db_session.query(DocumentEmbedding).filter(
                    DocumentEmbedding.service_id == service_id_str
                ).limit(limit * 5).all()
                
                # Simple keyword matching with scoring
                matches = []
                for emb in results:
                    content_lower = emb.content.lower()
                    matching_words = sum(1 for word in query_words if word in content_lower)
                    
                    if matching_words > 0:
                        score = matching_words / max(len(query_words), 1)
                        matches.append({
                            'id': str(emb.id),
                            'document_id': str(emb.document_id),
                            'chunk_index': emb.chunk_index,
                            'chunk_text': emb.content,
                            'similarity_score': min(0.9, 0.5 + score * 0.4)
                        })
                
                # Sort by score and limit
                matches.sort(key=lambda x: x['similarity_score'], reverse=True)
                return matches[:limit]
            except Exception as e2:
                print(f"❌ Fallback search also failed: {e2}")
                return []
    
    def get_status(self):
        """Get vector service status"""
        try:
            if self.db:
                embedding_count = self.db.query(DocumentEmbedding).count()
            else:
                embedding_count = 0
            
            return {
                'available': True,
                'status': 'operational',
                'embedding_count': embedding_count,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.embedding_dim,
                'ollama_url': self.ollama_url
            }
        except Exception as e:
            return {
                'available': False,
                'status': 'error',
                'error': str(e)
            }


class VectorService:
    """Simplified vector service interface"""
    
    def __init__(self):
        self.service = VectorDatabaseService()
    
    def generate_embedding(self, text):
        """Generate embedding for text"""
        return self.service.generate_embedding(text)
    
    def generate_embeddings_batch(self, texts):
        """Generate embeddings for multiple texts"""
        return self.service.generate_embeddings_batch(texts)
    
    def add_document_embeddings(self, document_id, service_id, chunks, db_session=None):
        """Add document embeddings"""
        self.service.db = db_session
        return self.service.add_document_embeddings(document_id, service_id, chunks, db_session)
    
    def search_similar_documents(self, query, service_id, limit=5, db_session=None):
        """Search similar documents"""
        return self.service.search_similar_documents(query, service_id, limit, db_session)
    
    def get_status(self):
        """Get service status"""
        return self.service.get_status()


def get_vector_service(db: Session = None):
    """Factory function to get vector service instance"""
    service = VectorDatabaseService(db)
    return service
