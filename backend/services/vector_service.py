"""
Vector Service using Supabase pgvector
Replaces ChromaDB with PostgreSQL pgvector extension
"""
import requests
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.sqlalchemy_models import DocumentEmbedding, Document, Service
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')

class VectorDatabaseService:
    """Vector database service using Supabase pgvector"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.ollama_url = OLLAMA_BASE_URL
        self.embedding_model = OLLAMA_EMBEDDING_MODEL
        self.embedding_dim = 768  # nomic-embed-text produces 768-dimensional vectors
        self._ollama_checked = False
        self._ollama_available = False
        
    def _check_ollama(self):
        """Check if Ollama service is available (lazy check)"""
        if self._ollama_checked:
            return self._ollama_available
            
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                print(f"[OK] Ollama available with models: {models}")
                self._ollama_available = True
            self._ollama_checked = True
        except Exception as e:
            print(f"[WARN] Ollama service unavailable: {e}")
            self._ollama_available = False
            self._ollama_checked = True
            
        return self._ollama_available
    
    def generate_embedding(self, text):
        """
        Generate embedding for text using Ollama
        Returns: list of floats (768 dimensions)
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embed",
                json={
                    "model": self.embedding_model,
                    "input": text
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()['embeddings'][0]
            else:
                print(f"Error generating embedding: {response.text}")
                return None
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
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
        Add document embeddings to pgvector
        Args:
            document_id: UUID of the document
            service_id: UUID of the service
            chunks: List of text chunks
            db_session: SQLAlchemy session
        Returns:
            List of created embedding IDs
        """
        embedding_ids = []
        try:
            for chunk_index, chunk in enumerate(chunks):
                # Generate embedding
                embedding_vector = self.generate_embedding(chunk)
                
                if not embedding_vector:
                    print(f"Failed to generate embedding for chunk {chunk_index}")
                    continue
                
                # Create embedding record
                doc_embedding = DocumentEmbedding(
                    id=__import__('uuid').uuid4(),
                    document_id=document_id,
                    service_id=service_id,
                    chunk_index=chunk_index,
                    chunk_text=chunk,
                    embedding=embedding_vector  # pgvector will handle the vector
                )
                
                db_session.add(doc_embedding)
                embedding_ids.append(doc_embedding.id)
            
            db_session.commit()
            return embedding_ids
            
        except Exception as e:
            db_session.rollback()
            print(f"Error adding embeddings: {e}")
            return []
    
    def search_similar_documents(self, query, service_id, limit=5, db_session=None):
        """
        Search for similar documents using pgvector cosine similarity
        Returns: List of similar chunks with relevance scores
        """
        if not db_session:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search using pgvector cosine similarity operator (<->)
            # The operator <-> computes cosine distance (smaller = more similar)
            results = db_session.execute(text(f"""
                SELECT 
                    id,
                    document_id,
                    service_id,
                    chunk_index,
                    chunk_text,
                    1 - (embedding <-> :query_embedding::vector) as similarity_score
                FROM document_embeddings
                WHERE service_id = :service_id
                ORDER BY embedding <-> :query_embedding::vector
                LIMIT :limit
            """), {
                "query_embedding": query_embedding,
                "service_id": str(service_id),
                "limit": limit
            }).fetchall()
            
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
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
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
