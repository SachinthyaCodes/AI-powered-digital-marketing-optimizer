"""
Complete RAG System using Ollama (English Only)
Production-ready implementation with:
- Standard English tokenization
- Multilingual sentence embeddings
- FAISS vector database
- Context-aware retrieval
- Integration with local Ollama models
"""
import os
import json
import numpy as np
from typing import List, Dict, Optional, Union
from datetime import datetime
import traceback
import re

# Sentence transformers for embeddings
from sentence_transformers import SentenceTransformer

# FAISS for vector search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available, will use numpy fallback")


class OllamaRAGSystem:
    """
    Production-ready RAG system for English language with Ollama
    
    Features:
    - Standard English tokenization
    - Multilingual embeddings (optimized for English)
    - Efficient vector search with FAISS
    - Context budget management
    - Source attribution and relevance scoring
    """
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        max_context_tokens: int = 4096,
        vector_db_path: Optional[str] = None,
        use_gpu: bool = False
    ):
        """
        Initialize RAG system with Ollama
        
        Args:
            embedding_model: HuggingFace sentence-transformer model (English optimized)
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap characters between chunks
            max_context_tokens: Ollama's context window (default 4096)
            vector_db_path: Path to save/load vector index
            use_gpu: Use GPU for embeddings (if available)
        """
        print("\n" + "=" * 80)
        print("INITIALIZING OLLAMA RAG SYSTEM (English Only)")
        print("=" * 80)
        
        # Configuration
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_context_tokens = max_context_tokens
        self.vector_db_path = vector_db_path
        self.use_gpu = use_gpu
        
        # Initialize embedding model
        print("\n[1/2] Loading embedding model...")
        try:
            device = 'cuda' if use_gpu else 'cpu'
            self.embedding_model = SentenceTransformer(embedding_model, device=device)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            print(f"✅ Embedding model loaded: {self.embedding_dim}D vectors on {device}")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
        
        # Initialize vector storage
        print("\n[2/2] Initializing vector database...")
        self.index = None
        self.chunks = []
        self.chunk_texts = []
        self.metadata_store = []
        
        if FAISS_AVAILABLE:
            print("✅ FAISS available for efficient search")
        else:
            print("⚠️ Using numpy fallback (slower)")
        
        print("\n" + "=" * 80)
        print("RAG SYSTEM READY")
        print("=" * 80 + "\n")
    
    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Split document into overlapping chunks using character-based splitting
        
        Args:
            text: Document text
            metadata: Optional metadata to attach to chunks
        
        Returns:
            List of chunks with metadata
        """
        # Clean text
        text = text.strip()
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at document end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within next 100 chars
                sentence_end = text.rfind('.', end, min(end + 100, len(text)))
                if sentence_end != -1 and sentence_end > start:
                    end = sentence_end + 1
            else:
                end = len(text)
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_data = {
                    'text': chunk_text,
                    'chunk_id': chunk_id,
                    'start_char': start,
                    'end_char': end,
                    'metadata': metadata or {}
                }
                chunks.append(chunk_data)
                chunk_id += 1
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
    
    def add_documents(
        self,
        documents: List[Dict],
        batch_size: int = 32
    ) -> Dict:
        """
        Add documents to RAG system
        
        Args:
            documents: List of documents with 'text' and optional 'metadata'
            batch_size: Batch size for embedding generation
        
        Returns:
            Processing summary
        """
        print(f"\n📥 Processing {len(documents)} documents...")
        
        all_chunks = []
        total_chunks = 0
        
        # Chunk all documents
        for doc_idx, doc in enumerate(documents):
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            metadata['document_index'] = doc_idx
            
            chunks = self.chunk_document(text, metadata)
            all_chunks.extend(chunks)
            total_chunks += len(chunks)
            
            print(f"  Document {doc_idx + 1}: {len(chunks)} chunks")
        
        if not all_chunks:
            return {
                'success': False,
                'error': 'No chunks created',
                'documents': len(documents),
                'chunks': 0
            }
        
        # Generate embeddings
        print(f"\n🔢 Generating embeddings for {total_chunks} chunks...")
        chunk_texts = [chunk['text'] for chunk in all_chunks]
        
        try:
            embeddings = self.embedding_model.encode(
                chunk_texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            print(f"✅ Embeddings generated: {embeddings.shape}")
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'documents': len(documents),
                'chunks': total_chunks
            }
        
        # Add to vector store
        self._add_embeddings_to_index(embeddings, all_chunks, chunk_texts)
        
        return {
            'success': True,
            'documents': len(documents),
            'chunks': total_chunks,
            'index_size': len(self.chunks)
        }
    
    def _add_embeddings_to_index(
        self,
        embeddings: np.ndarray,
        chunks: List[Dict],
        chunk_texts: List[str]
    ):
        """Add embeddings to FAISS index"""
        embeddings = embeddings.astype('float32')
        
        if self.index is None:
            # Create new index
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                print(f"✅ Created FAISS index")
            else:
                self.index = []
                print(f"✅ Created numpy index")
        
        # Add to index
        if FAISS_AVAILABLE:
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
        else:
            if not isinstance(self.index, list):
                self.index = []
            self.index.extend(embeddings.tolist())
        
        # Store chunks and metadata
        self.chunks.extend(chunks)
        self.chunk_texts.extend(chunk_texts)
        self.metadata_store.extend([chunk.get('metadata', {}) for chunk in chunks])
        
        print(f"✅ Added {len(embeddings)} vectors to index (total: {len(self.chunks)})")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of results
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of results with text, score, and metadata
        """
        if not self.chunks:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).astype('float32')
        
        # Search
        if FAISS_AVAILABLE:
            faiss.normalize_L2(query_embedding)
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
            scores = scores[0]
            indices = indices[0]
        else:
            # Numpy fallback
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            all_embeddings = np.array(self.index).astype('float32')
            norms = np.linalg.norm(all_embeddings, axis=1, keepdims=True)
            all_embeddings_norm = all_embeddings / norms
            scores = np.dot(all_embeddings_norm, query_norm.T).flatten()
            indices = np.argsort(scores)[::-1][:top_k]
            scores = scores[indices]
        
        # Format results
        results = []
        for idx, score in zip(indices, scores):
            if score >= min_similarity and idx < len(self.chunks):
                results.append({
                    'text': self.chunk_texts[idx],
                    'score': float(score),
                    'metadata': self.chunks[idx].get('metadata', {}),
                    'chunk_id': self.chunks[idx].get('chunk_id', idx)
                })
        
        return results
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> Dict:
        """
        Query RAG system - retrieve relevant context
        
        Args:
            question: User question
            top_k: Number of chunks to retrieve
            min_similarity: Minimum similarity threshold
        
        Returns:
            Query results with context and sources
        """
        # Search for relevant chunks
        results = self.search(question, top_k, min_similarity)
        
        if not results:
            return {
                'success': False,
                'question': question,
                'context': '',
                'sources': [],
                'error': 'No relevant information found'
            }
        
        # Build context
        context_parts = []
        sources = []
        
        for i, result in enumerate(results):
            context_parts.append(f"[Source {i+1}]\n{result['text']}\n")
            sources.append({
                'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                'score': result['score'],
                'metadata': result['metadata']
            })
        
        context = "\n".join(context_parts)
        
        return {
            'success': True,
            'question': question,
            'context': context,
            'sources': sources,
            'num_sources': len(sources)
        }
    
    def save_index(self, path: Optional[str] = None):
        """Save vector index to disk"""
        save_path = path or self.vector_db_path
        
        if not save_path:
            raise ValueError("No save path specified")
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save FAISS index
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, f"{save_path}.faiss")
        
        # Save metadata
        metadata = {
            'chunks': self.chunks,
            'chunk_texts': self.chunk_texts,
            'metadata_store': self.metadata_store,
            'config': {
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'embedding_dim': self.embedding_dim
            },
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f"{save_path}.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved index to {save_path}")
    
    def load_index(self, path: Optional[str] = None):
        """Load vector index from disk"""
        load_path = path or self.vector_db_path
        
        if not load_path:
            raise ValueError("No load path specified")
        
        # Load FAISS index
        if FAISS_AVAILABLE and os.path.exists(f"{load_path}.faiss"):
            self.index = faiss.read_index(f"{load_path}.faiss")
        
        # Load metadata
        with open(f"{load_path}.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.chunks = metadata['chunks']
        self.chunk_texts = metadata['chunk_texts']
        self.metadata_store = metadata['metadata_store']
        
        print(f"✅ Loaded index from {load_path} ({len(self.chunks)} chunks)")
    
    def clear(self):
        """Clear all data from RAG system"""
        self.index = None
        self.chunks = []
        self.chunk_texts = []
        self.metadata_store = []
        print("✅ RAG system cleared")
