"""
Complete Sinhala RAG System using SinLlama
Production-ready implementation with:
- SinLlama Extended Tokenizer (139K vocab)
- Multilingual sentence embeddings
- FAISS vector database
- Context-aware retrieval
- Integration with local SinLlama GGUF model
"""
import os
import json
import numpy as np
from typing import List, Dict, Optional, Union
from datetime import datetime
import traceback

# Import SinLlama tokenizer
from services.sinllama_tokenizer import get_tokenizer

# Sentence transformers for embeddings
from sentence_transformers import SentenceTransformer

# FAISS for vector search
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not available, will use numpy fallback")


class SinhalaRAGSystem:
    """
    Production-ready RAG system for Sinhala language with SinLlama
    
    Features:
    - Token-aware document chunking using SinLlama tokenizer
    - Multilingual embeddings (Sinhala + English)
    - Efficient vector search with FAISS
    - Context budget management for 2048 token limit
    - Source attribution and relevance scoring
    """
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        max_context_tokens: int = 2048,
        vector_db_path: Optional[str] = None,
        use_gpu: bool = False
    ):
        """
        Initialize RAG system
        
        Args:
            embedding_model: HuggingFace sentence-transformer model
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap tokens between chunks
            max_context_tokens: SinLlama's context window (2048)
            vector_db_path: Path to save/load vector index
            use_gpu: Use GPU for embeddings (if available)
        """
        print("\n" + "=" * 80)
        print("INITIALIZING SINHALA RAG SYSTEM")
        print("=" * 80)
        
        # Configuration
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_context_tokens = max_context_tokens
        self.vector_db_path = vector_db_path
        self.use_gpu = use_gpu
        
        # 1. Initialize SinLlama tokenizer
        print("\n[1/3] Loading SinLlama Extended Tokenizer...")
        self.tokenizer = get_tokenizer()
        print(f"✅ Tokenizer ready: {len(self.tokenizer):,} tokens")
        
        # 2. Initialize embedding model
        print("\n[2/3] Loading embedding model...")
        try:
            device = 'cuda' if use_gpu else 'cpu'
            self.embedding_model = SentenceTransformer(embedding_model, device=device)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            print(f"✅ Embedding model loaded: {self.embedding_dim}D vectors on {device}")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
        
        # 3. Initialize vector storage
        print("\n[3/3] Initializing vector database...")
        self.index = None
        self.chunks = []
        self.chunk_texts = []
        self.metadata_store = []
        
        if FAISS_AVAILABLE:
            print("✅ FAISS available for efficient search")
        else:
            print("⚠️ Using numpy fallback (slower)")
        
        print("\n" + "=" * 80)
        print("✅ RAG SYSTEM READY!")
        print(f"   Tokenizer: {len(self.tokenizer):,} vocab")
        print(f"   Chunk size: {chunk_size} tokens (overlap: {chunk_overlap})")
        print(f"   Embedding: {self.embedding_dim}D")
        print(f"   Context limit: {max_context_tokens} tokens")
        print("=" * 80 + "\n")
    
    # ═══════════════════════════════════════════════════════════════════
    # DOCUMENT PROCESSING
    # ═══════════════════════════════════════════════════════════════════
    
    def chunk_document(
        self, 
        text: str, 
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Split document into token-aware chunks
        
        STEP 1 in RAG: Document Processing
        
        Args:
            text: Document text
            metadata: Optional metadata (doc_id, filename, etc.)
        
        Returns:
            List of chunk dictionaries
        """
        return self.tokenizer.chunk_document(
            text=text,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            metadata=metadata
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        batch_size: int = 32
    ) -> Dict:
        """
        Add documents to RAG system
        
        STEP 2 in RAG: Index Documents
        
        Args:
            documents: List of document texts
            metadata: Optional list of metadata dicts
            batch_size: Batch size for embedding generation
        
        Returns:
            Statistics about indexing
        """
        if not documents:
            return {'error': 'No documents provided'}
        
        if metadata is None:
            metadata = [{'doc_id': i} for i in range(len(documents))]
        
        print(f"\n{'=' * 80}")
        print(f"ADDING {len(documents)} DOCUMENTS TO RAG")
        print('=' * 80)
        
        # 1. Chunk all documents
        print("\n[1/4] Chunking documents with SinLlama tokenizer...")
        all_chunks = []
        chunk_stats = []
        
        for i, (doc, meta) in enumerate(zip(documents, metadata)):
            if 'doc_id' not in meta:
                meta['doc_id'] = i
            
            doc_chunks = self.chunk_document(doc, meta)
            all_chunks.extend(doc_chunks)
            
            chunk_stats.append({
                'doc_id': meta['doc_id'],
                'doc_length': len(doc),
                'num_chunks': len(doc_chunks),
                'avg_tokens': np.mean([c['num_tokens'] for c in doc_chunks]) if doc_chunks else 0
            })
            
            print(f"  Doc {i+1}: {len(doc_chunks)} chunks " +
                  f"({sum(c['num_tokens'] for c in doc_chunks)} tokens)")
        
        self.chunks = all_chunks
        self.chunk_texts = [c['text'] for c in all_chunks]
        self.metadata_store = [c['metadata'] for c in all_chunks]
        
        print(f"\n✅ Total chunks: {len(self.chunk_texts)}")
        print(f"   Avg tokens/chunk: {np.mean([c['num_tokens'] for c in all_chunks]):.1f}")
        
        # 2. Generate embeddings
        print("\n[2/4] Generating embeddings with multilingual model...")
        try:
            embeddings = self.embedding_model.encode(
                self.chunk_texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True  # For cosine similarity
            )
            print(f"✅ Generated {embeddings.shape[0]} embeddings ({embeddings.shape[1]}D)")
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            traceback.print_exc()
            return {'error': f'Embedding generation failed: {str(e)}'}
        
        # 3. Build vector index
        print("\n[3/4] Building vector index...")
        try:
            if FAISS_AVAILABLE:
                # Use FAISS for efficient search
                self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product (cosine sim)
                self.index.add(embeddings.astype('float32'))
                print(f"✅ FAISS index built: {self.index.ntotal} vectors")
            else:
                # Fallback to numpy
                self.index = embeddings
                print(f"✅ Numpy index built: {self.index.shape[0]} vectors")
        except Exception as e:
            print(f"❌ Index building failed: {e}")
            traceback.print_exc()
            return {'error': f'Index building failed: {str(e)}'}
        
        # 4. Save if path provided
        if self.vector_db_path:
            print("\n[4/4] Saving index to disk...")
            try:
                self.save_index()
                print(f"✅ Index saved to {self.vector_db_path}")
            except Exception as e:
                print(f"⚠️ Failed to save index: {e}")
        
        print("\n" + "=" * 80)
        print("✅ DOCUMENTS INDEXED SUCCESSFULLY!")
        print("=" * 80 + "\n")
        
        return {
            'success': True,
            'num_documents': len(documents),
            'num_chunks': len(all_chunks),
            'total_tokens': sum(c['num_tokens'] for c in all_chunks),
            'avg_chunks_per_doc': len(all_chunks) / len(documents),
            'embedding_dim': self.embedding_dim,
            'chunk_stats': chunk_stats
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # RETRIEVAL
    # ═══════════════════════════════════════════════════════════════════
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict]:
        """
        Search for relevant chunks
        
        STEP 3 in RAG: Retrieve Relevant Context
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score
        
        Returns:
            List of relevant chunks with scores
        """
        if self.index is None:
            raise ValueError("No documents indexed! Call add_documents() first.")
        
        if not query:
            return []
        
        # 1. Encode query
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        # 2. Search
        if FAISS_AVAILABLE and isinstance(self.index, faiss.Index):
            # FAISS search
            scores, indices = self.index.search(
                query_embedding.astype('float32'), 
                min(top_k, self.index.ntotal)
            )
            scores = scores[0]
            indices = indices[0]
        else:
            # Numpy fallback
            similarities = np.dot(self.index, query_embedding.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k]
            scores = similarities[top_indices]
            indices = top_indices
        
        # 3. Format results
        results = []
        for score, idx in zip(scores, indices):
            if idx >= len(self.chunks):
                continue
            
            if score < min_score:
                continue
            
            # Determine relevance level
            if score > 0.7:
                relevance = 'high'
            elif score > 0.5:
                relevance = 'medium'
            elif score > 0.3:
                relevance = 'low'
            else:
                relevance = 'very_low'
            
            results.append({
                'chunk_id': self.chunks[idx]['id'],
                'text': self.chunk_texts[idx],
                'score': float(score),
                'relevance': relevance,
                'metadata': self.metadata_store[idx],
                'num_tokens': self.chunks[idx]['num_tokens']
            })
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════
    # CONTEXT PREPARATION
    # ═══════════════════════════════════════════════════════════════════
    
    def prepare_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict],
        system_message: Optional[str] = None,
        language: str = 'si'  # 'si' for Sinhala, 'en' for English
    ) -> Dict:
        """
        Prepare final prompt for SinLlama
        
        STEP 4 in RAG: Build Context-Aware Prompt
        
        Args:
            query: User's question
            retrieved_chunks: Retrieved chunk dictionaries
            system_message: Optional system message
            language: Response language ('si' or 'en')
        
        Returns:
            Prompt data with token counts
        """
        # Extract chunk texts
        chunk_texts = [c['text'] for c in retrieved_chunks]
        
        # Default system messages
        if system_message is None:
            if language == 'si':
                system_message = "ඔබ උපකාර කරන AI සහායකයෙකි. පහත සන්දර්භය භාවිතා කරමින් ප්‍රශ්නයට නිවැරදිව සිංහලෙන් පිළිතුරු දෙන්න."
            else:
                system_message = "You are a helpful AI assistant. Answer the question accurately using the context provided below."
        
        # Use tokenizer to prepare context
        prepared = self.tokenizer.prepare_context_for_generation(
            query=query,
            retrieved_chunks=chunk_texts,
            max_context_tokens=self.max_context_tokens,
            system_message=system_message
        )
        
        # Add chunk metadata
        prepared['sources'] = [
            {
                'chunk_id': c['chunk_id'],
                'score': c['score'],
                'relevance': c['relevance'],
                'metadata': c['metadata'],
                'text_preview': c['text'][:200] + '...' if len(c['text']) > 200 else c['text']
            }
            for c in retrieved_chunks[:prepared['chunks_used']]
        ]
        
        return prepared
    
    # ═══════════════════════════════════════════════════════════════════
    # END-TO-END QUERY
    # ═══════════════════════════════════════════════════════════════════
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        min_score: float = 0.3,
        language: str = 'si',
        return_prompt: bool = True
    ) -> Dict:
        """
        Complete RAG query: retrieve + prepare prompt
        
        THIS IS THE MAIN METHOD YOU'LL USE!
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score
            language: Response language ('si' or 'en')
            return_prompt: Include full prompt in response
        
        Returns:
            Complete RAG response with prompt and sources
        """
        try:
            # 1. Retrieve relevant chunks
            results = self.search(question, top_k=top_k, min_score=min_score)
            
            if not results:
                return {
                    'success': False,
                    'error': 'No relevant documents found',
                    'question': question,
                    'chunks_retrieved': 0
                }
            
            # 2. Prepare prompt
            prompt_data = self.prepare_prompt(
                query=question,
                retrieved_chunks=results,
                language=language
            )
            
            # 3. Compile response
            response = {
                'success': True,
                'question': question,
                'chunks_retrieved': len(results),
                'chunks_used': prompt_data['chunks_used'],
                'prompt_tokens': prompt_data['prompt_tokens'],
                'context_tokens': prompt_data['context_tokens'],
                'tokens_remaining': prompt_data['tokens_remaining'],
                'within_limit': prompt_data['within_limit'],
                'sources': prompt_data['sources'],
                'language': language
            }
            
            if return_prompt:
                response['prompt'] = prompt_data['prompt']
            
            # Add relevance summary
            relevance_counts = {}
            for r in results:
                rel = r['relevance']
                relevance_counts[rel] = relevance_counts.get(rel, 0) + 1
            
            response['relevance_distribution'] = relevance_counts
            
            return response
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'question': question
            }
    
    # ═══════════════════════════════════════════════════════════════════
    # PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════
    
    def save_index(self, path: Optional[str] = None):
        """Save vector index and chunks to disk"""
        path = path or self.vector_db_path
        if not path:
            raise ValueError("No path provided for saving index")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        # Save FAISS index or numpy array
        if FAISS_AVAILABLE and isinstance(self.index, faiss.Index):
            faiss.write_index(self.index, f"{path}.faiss")
        else:
            np.save(f"{path}.npy", self.index)
        
        # Save chunks and metadata
        data = {
            'chunks': self.chunks,
            'chunk_texts': self.chunk_texts,
            'metadata_store': self.metadata_store,
            'config': {
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'max_context_tokens': self.max_context_tokens,
                'embedding_dim': self.embedding_dim,
                'saved_at': datetime.now().isoformat()
            }
        }
        
        with open(f"{path}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Index saved to {path}")
    
    def load_index(self, path: Optional[str] = None):
        """Load vector index and chunks from disk"""
        path = path or self.vector_db_path
        if not path:
            raise ValueError("No path provided for loading index")
        
        # Load FAISS index or numpy array
        if os.path.exists(f"{path}.faiss"):
            self.index = faiss.read_index(f"{path}.faiss")
            print(f"✅ Loaded FAISS index: {self.index.ntotal} vectors")
        elif os.path.exists(f"{path}.npy"):
            self.index = np.load(f"{path}.npy")
            print(f"✅ Loaded numpy index: {self.index.shape[0]} vectors")
        else:
            raise FileNotFoundError(f"No index found at {path}")
        
        # Load chunks and metadata
        with open(f"{path}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.chunks = data['chunks']
        self.chunk_texts = data['chunk_texts']
        self.metadata_store = data['metadata_store']
        
        config = data.get('config', {})
        print(f"✅ Loaded {len(self.chunks)} chunks")
        print(f"   Saved at: {config.get('saved_at', 'unknown')}")
    
    # ═══════════════════════════════════════════════════════════════════
    # STATISTICS & ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        if not self.chunks:
            return {'error': 'No documents indexed'}
        
        token_counts = [c['num_tokens'] for c in self.chunks]
        
        return {
            'num_chunks': len(self.chunks),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_chunk': np.mean(token_counts),
            'std_tokens': np.std(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'embedding_dim': self.embedding_dim,
            'index_size': self.index.ntotal if FAISS_AVAILABLE and isinstance(self.index, faiss.Index) else len(self.index),
            'config': {
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'max_context_tokens': self.max_context_tokens
            }
        }


# ═══════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def create_rag_system(
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    vector_db_path: Optional[str] = None
) -> SinhalaRAGSystem:
    """
    Create a ready-to-use RAG system
    
    Args:
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Overlap between chunks
        vector_db_path: Path for saving/loading index
    
    Returns:
        SinhalaRAGSystem instance
    """
    return SinhalaRAGSystem(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        vector_db_path=vector_db_path
    )


# ═══════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SINHALA RAG SYSTEM DEMONSTRATION")
    print("=" * 80)
    
    # Create RAG system
    rag = create_rag_system(
        chunk_size=512,
        chunk_overlap=50,
        vector_db_path="./data/rag_index"
    )
    
    # Example documents (Sinhala)
    documents = [
        """ශ්‍රී ලංකාව දකුණු ආසියාවේ පිහිටි දිවයින රටකි. එය ඉන්දියානු සාගරයේ පිහිටා ඇත. 
        ශ්‍රී ලංකාවේ ජනගහනය මිලියන 22 කි. කොළඹ ශ්‍රී ලංකාවේ වාණිජ අගනුවර වන අතර 
        ශ්‍රී ජයවර්ධනපුර කෝට්ටේ නිල අගනුවර වේ.""",
        
        """සිංහල භාෂාව ශ්‍රී ලංකාවේ නිල භාෂාවකි. සිංහල භාෂාව කතා කරන්නේ මිලියන 17ක් 
        පමණ ජනතාවක් විසිනි. සිංහල හෝඩිය අද්විතීය හා සුන්දර වේ.""",
        
        """ශ්‍රී ලංකාවේ ප්‍රධාන කර්මාන්ත අතර තේ, රබර්, පොල් සහ ගාර්මන්ට් ඇතුළත් වේ. 
        තේ කර්මාන්තය ශ්‍රී ලංකාවේ ප්‍රධානතම අපනයන ආදායම් මාර්ගයකි."""
    ]
    
    # Add documents
    stats = rag.add_documents(documents)
    print(f"\n✅ Indexed {stats['num_documents']} documents into {stats['num_chunks']} chunks")
    
    # Query the system
    questions = [
        "ශ්‍රී ලංකාවේ අගනුවර කුමක්ද?",
        "සිංහල භාෂාව කීදෙනෙකු කතා කරනවාද?",
        "ශ්‍රී ලංකාවේ ප්‍රධාන කර්මාන්ත මොනවාද?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─' * 80}")
        print(f"QUESTION {i}: {question}")
        print('─' * 80)
        
        result = rag.query(question, top_k=3, return_prompt=False)
        
        if result['success']:
            print(f"\n✅ Retrieved {result['chunks_retrieved']} chunks")
            print(f"✅ Used {result['chunks_used']} chunks in context")
            print(f"✅ Prompt: {result['prompt_tokens']} tokens")
            print(f"✅ Remaining: {result['tokens_remaining']} tokens")
            
            print("\nTop sources:")
            for j, source in enumerate(result['sources'], 1):
                print(f"\n  {j}. [{source['relevance']}] Score: {source['score']:.3f}")
                print(f"     {source['text_preview']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 80)
    print("✅ RAG SYSTEM DEMONSTRATION COMPLETE!")
    print("=" * 80 + "\n")
