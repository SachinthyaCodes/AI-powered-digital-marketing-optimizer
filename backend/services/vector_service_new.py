"""
Vector Service using Complete RAG System with SinLlama
Replaces old pgvector implementation with proper SinLlama tokenizer + embeddings
"""
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from services.complete_rag_system import SinhalaRAGSystem
from services.sinllama_service import get_sinllama_service


class VectorService:
    """
    Vector service using SinLlama RAG system
    Handles document indexing, retrieval, and answer generation
    """
    
    def __init__(self, service_id: Optional[str] = None):
        """
        Initialize vector service for a specific service/business
        
        Args:
            service_id: Optional service ID for multi-tenant support
        """
        self.service_id = service_id
        self.rag_system = None
        self.sinllama = get_sinllama_service()
        
        # Vector DB path for this service
        if service_id:
            self.vector_db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'rag_indices',
                f'service_{service_id}'
            )
        else:
            self.vector_db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'rag_indices',
                'default'
            )
        
        # Create directory if needed
        os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)
    
    def _get_rag_system(self) -> SinhalaRAGSystem:
        """Get or create RAG system instance"""
        if self.rag_system is None:
            self.rag_system = SinhalaRAGSystem(
                chunk_size=512,
                chunk_overlap=50,
                max_context_tokens=2048,
                vector_db_path=self.vector_db_path,
                use_gpu=False  # CPU only for now
            )
            
            # Try to load existing index
            try:
                if os.path.exists(f"{self.vector_db_path}.json"):
                    self.rag_system.load_index()
                    print(f"✅ Loaded existing RAG index for service {self.service_id}")
            except Exception as e:
                print(f"⚠️ No existing index found: {e}")
        
        return self.rag_system
    
    def add_documents(
        self, 
        documents: List[str], 
        metadata: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Add documents to vector database
        
        Args:
            documents: List of document texts
            metadata: Optional metadata for each document
        
        Returns:
            Indexing statistics
        """
        rag = self._get_rag_system()
        return rag.add_documents(documents, metadata)
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        min_score: float = 0.3
    ) -> List[Dict]:
        """
        Search for relevant document chunks
        
        Args:
            query: Search query
            top_k: Number of results
            min_score: Minimum similarity score
        
        Returns:
            List of relevant chunks with scores
        """
        rag = self._get_rag_system()
        return rag.search(query, top_k, min_score)
    
    def query_with_rag(
        self,
        question: str,
        top_k: int = 5,
        min_score: float = 0.3,
        language: str = 'si',
        generate_answer: bool = True
    ) -> Dict:
        """
        Complete RAG workflow: retrieve + generate answer
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score
            language: Response language ('si' or 'en')
            generate_answer: Whether to generate answer with SinLlama
        
        Returns:
            Complete response with answer and sources
        """
        try:
            # 1. RAG retrieval
            rag = self._get_rag_system()
            rag_result = rag.query(
                question=question,
                top_k=top_k,
                min_score=min_score,
                language=language,
                return_prompt=True
            )
            
            if not rag_result['success']:
                return rag_result
            
            # 2. Generate answer with SinLlama if requested
            if generate_answer:
                generation_result = self.sinllama.generate_rag_response(
                    prompt=rag_result['prompt'],
                    max_tokens=512,
                    temperature=0.7,
                    language=language
                )
                
                if generation_result['success']:
                    rag_result['answer'] = generation_result['response']
                    rag_result['generation_tokens'] = generation_result['tokens_used']
                else:
                    rag_result['answer'] = generation_result['response']
                    rag_result['generation_error'] = generation_result.get('error', '')
            
            return rag_result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'question': question
            }
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        try:
            rag = self._get_rag_system()
            return rag.get_stats()
        except Exception as e:
            return {'error': str(e)}
    
    def reset_index(self):
        """Reset/clear the vector index"""
        self.rag_system = None
        
        # Delete index files if they exist
        for ext in ['.faiss', '.npy', '.json']:
            path = f"{self.vector_db_path}{ext}"
            if os.path.exists(path):
                os.remove(path)
                print(f"✅ Deleted {path}")


# Legacy compatibility functions for existing code
class VectorDatabaseService:
    """Legacy wrapper for backward compatibility"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.vector_service = VectorService()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding (legacy method)"""
        # This is now handled internally by RAG system
        print("⚠️ generate_embedding is deprecated, use VectorService.add_documents instead")
        return [0.0] * 768
    
    def search_similar(self, query: str, service_id: str, top_k: int = 5) -> List[Dict]:
        """Search similar documents (legacy method)"""
        print("⚠️ search_similar is deprecated, use VectorService.query_with_rag instead")
        vs = VectorService(service_id)
        return vs.search(query, top_k)
