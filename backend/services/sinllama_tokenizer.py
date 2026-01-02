"""
SinLlama Extended Tokenizer Module
Uses the Extended-Sinhala-LLaMA tokenizer from HuggingFace (polyglots/Extended-Sinhala-LLaMA)
139,336 tokens vocabulary optimized for Sinhala language
"""
import os
from transformers import AutoTokenizer
from typing import List, Dict, Optional, Union
import numpy as np

# HuggingFace token for authentication
HF_TOKEN = "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"

class SinLlamaTokenizer:
    """
    Extended Sinhala tokenizer for SinLlama model
    Vocabulary: 139,336 tokens (128,256 base + ~11,080 Sinhala-specific)
    """
    
    _instance = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SinLlamaTokenizer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._tokenizer is None:
            self._load_tokenizer()
    
    def _load_tokenizer(self):
        """Load the Extended-Sinhala-LLaMA tokenizer from HuggingFace"""
        try:
            print("\n" + "=" * 80)
            print("Loading SinLlama Extended Tokenizer")
            print("=" * 80)
            print("Model: polyglots/Extended-Sinhala-LLaMA")
            print("Vocabulary: 139,336 tokens (optimized for Sinhala)")
            
            # Load from HuggingFace with authentication
            self._tokenizer = AutoTokenizer.from_pretrained(
                "polyglots/Extended-Sinhala-LLaMA",
                token=HF_TOKEN,
                trust_remote_code=True
            )
            
            vocab_size = len(self._tokenizer)
            print(f"\n✅ Tokenizer loaded successfully!")
            print(f"   Vocabulary size: {vocab_size:,} tokens")
            print(f"   Model max length: {self._tokenizer.model_max_length:,}")
            print("=" * 80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Failed to load SinLlama tokenizer: {e}")
            print("Falling back to base tokenizer...")
            # Fallback to base LLaMA tokenizer if extended version fails
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(
                    "meta-llama/Llama-2-7b-hf",
                    token=HF_TOKEN
                )
                print("✅ Fallback tokenizer loaded")
            except:
                raise RuntimeError("Failed to load any tokenizer")
    
    @property
    def tokenizer(self):
        """Get the underlying HuggingFace tokenizer"""
        return self._tokenizer
    
    def __len__(self):
        """Return vocabulary size"""
        return len(self._tokenizer)
    
    # ══════════════════════════════════════════════════════════════════
    # BASIC TOKENIZATION
    # ══════════════════════════════════════════════════════════════════
    
    def encode(
        self, 
        text: str, 
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        truncation: bool = False,
        padding: bool = False
    ) -> List[int]:
        """
        Encode text to token IDs
        
        Args:
            text: Input text (Sinhala or English)
            add_special_tokens: Add BOS/EOS tokens
            max_length: Maximum sequence length
            truncation: Truncate if exceeds max_length
            padding: Pad to max_length
        
        Returns:
            List of token IDs
        """
        if not text:
            return []
        
        result = self._tokenizer.encode(
            text,
            add_special_tokens=add_special_tokens,
            max_length=max_length,
            truncation=truncation,
            padding='max_length' if padding else False,
            return_tensors=None  # Return list, not tensor
        )
        
        return result
    
    def decode(
        self, 
        token_ids: List[int], 
        skip_special_tokens: bool = True
    ) -> str:
        """
        Decode token IDs back to text
        
        Args:
            token_ids: List of token IDs
            skip_special_tokens: Remove BOS/EOS/PAD tokens
        
        Returns:
            Decoded text string
        """
        if not token_ids:
            return ""
        
        return self._tokenizer.decode(
            token_ids,
            skip_special_tokens=skip_special_tokens
        )
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into string tokens (for inspection)
        
        Args:
            text: Input text
        
        Returns:
            List of token strings
        """
        return self._tokenizer.tokenize(text)
    
    # ══════════════════════════════════════════════════════════════════
    # RAG-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════
    
    def chunk_document(
        self, 
        text: str, 
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Split document into token-aware chunks for RAG
        
        This is STEP 1 in RAG pipeline: Document Processing
        
        Args:
            text: Document text to chunk
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlapping tokens between chunks
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of chunk dictionaries with text, tokens, and metadata
        """
        if not text:
            return []
        
        # Encode entire document
        tokens = self.encode(text, add_special_tokens=False)
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(tokens):
            # Extract chunk tokens
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.decode(chunk_tokens, skip_special_tokens=True)
            
            # Create chunk dictionary
            chunk = {
                'id': chunk_id,
                'text': chunk_text,
                'tokens': chunk_tokens,
                'num_tokens': len(chunk_tokens),
                'start_pos': start,
                'end_pos': end,
                'metadata': metadata or {}
            }
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - chunk_overlap
            chunk_id += 1
            
            # Safety: prevent infinite loop
            if end >= len(tokens):
                break
        
        return chunks
    
    def prepare_for_embedding(
        self, 
        texts: Union[str, List[str]],
        max_length: int = 512
    ) -> Dict:
        """
        Prepare text(s) for embedding generation
        
        This is STEP 2 in RAG pipeline: Embedding Preparation
        
        Args:
            texts: Single text or list of texts
            max_length: Maximum sequence length
        
        Returns:
            Dictionary with input_ids, attention_mask for embedding model
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Batch encode with padding and truncation
        encoded = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt'  # Return PyTorch tensors
        )
        
        return {
            'input_ids': encoded['input_ids'],
            'attention_mask': encoded['attention_mask'],
            'num_texts': len(texts),
            'max_tokens': encoded['input_ids'].shape[1]
        }
    
    def prepare_context_for_generation(
        self,
        query: str,
        retrieved_chunks: List[str],
        max_context_tokens: int = 2048,
        system_message: Optional[str] = None
    ) -> Dict:
        """
        Prepare final prompt with retrieved context for SinLlama generation
        
        This is STEP 4 in RAG pipeline: Context Preparation
        
        Args:
            query: User's question
            retrieved_chunks: Retrieved document chunks
            max_context_tokens: Maximum total tokens (SinLlama context limit)
            system_message: Optional system message
        
        Returns:
            Dictionary with prompt, token counts, and metadata
        """
        # Default Sinhala system message
        if system_message is None:
            system_message = "ඔබ උපකාර කරන සහායකයෙකි. පහත සන්දර්භය භාවිතා කරමින් ප්‍රශ්නයට නිවැරදිව පිළිතුරු දෙන්න."
        
        # Calculate token budgets
        system_tokens = len(self.encode(system_message, add_special_tokens=False))
        query_tokens = len(self.encode(query, add_special_tokens=False))
        
        # Reserve tokens for formatting and generation
        formatting_tokens = 100  # For "සන්දර්භය:", "ප්‍රශ්නය:", etc.
        generation_buffer = 512  # Space for model response
        safety_buffer = 50
        
        available_for_context = (
            max_context_tokens 
            - system_tokens 
            - query_tokens 
            - formatting_tokens 
            - generation_buffer
            - safety_buffer
        )
        
        # Add chunks until we run out of budget
        selected_chunks = []
        used_tokens = 0
        
        for chunk in retrieved_chunks:
            chunk_tokens = len(self.encode(chunk, add_special_tokens=False))
            
            if used_tokens + chunk_tokens > available_for_context:
                break
            
            selected_chunks.append(chunk)
            used_tokens += chunk_tokens
        
        # Build final prompt in Sinhala format
        context = "\n\n".join(selected_chunks)
        
        prompt = f"""{system_message}

සන්දර්භය:
{context}

ප්‍රශ්නය: {query}

පිළිතුර:"""
        
        # Calculate actual token usage
        prompt_tokens = len(self.encode(prompt, add_special_tokens=True))
        
        return {
            'prompt': prompt,
            'query': query,
            'system_message': system_message,
            'chunks_used': len(selected_chunks),
            'chunks_available': len(retrieved_chunks),
            'prompt_tokens': prompt_tokens,
            'context_tokens': used_tokens,
            'tokens_remaining': max_context_tokens - prompt_tokens,
            'within_limit': prompt_tokens < max_context_tokens
        }
    
    # ══════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ══════════════════════════════════════════════════════════════════
    
    def count_tokens(self, text: str) -> int:
        """
        Count number of tokens in text
        
        Args:
            text: Input text
        
        Returns:
            Number of tokens
        """
        return len(self.encode(text, add_special_tokens=False))
    
    def analyze_tokenization(self, text: str) -> Dict:
        """
        Analyze how text is tokenized (for debugging/optimization)
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with tokenization statistics
        """
        tokens_list = self.tokenize(text)
        token_ids = self.encode(text, add_special_tokens=False)
        
        return {
            'text': text,
            'text_length': len(text),
            'num_tokens': len(token_ids),
            'tokens': tokens_list[:20],  # First 20 tokens
            'token_ids': token_ids[:20],  # First 20 IDs
            'compression_ratio': len(text) / max(len(token_ids), 1),
            'avg_chars_per_token': len(text) / max(len(token_ids), 1)
        }
    
    def compare_efficiency(self, texts: List[str]) -> Dict:
        """
        Compare tokenization efficiency across multiple texts
        Useful for determining optimal chunk sizes
        
        Args:
            texts: List of text samples
        
        Returns:
            Statistical analysis of tokenization
        """
        stats = []
        
        for text in texts:
            token_count = self.count_tokens(text)
            stats.append({
                'text_length': len(text),
                'token_count': token_count,
                'compression_ratio': len(text) / max(token_count, 1)
            })
        
        # Calculate aggregate statistics
        token_counts = [s['token_count'] for s in stats]
        compression_ratios = [s['compression_ratio'] for s in stats]
        
        return {
            'num_samples': len(texts),
            'total_tokens': sum(token_counts),
            'avg_tokens_per_text': np.mean(token_counts),
            'std_tokens': np.std(token_counts),
            'min_tokens': min(token_counts),
            'max_tokens': max(token_counts),
            'avg_compression': np.mean(compression_ratios),
            'details': stats
        }


# ══════════════════════════════════════════════════════════════════════
# GLOBAL TOKENIZER INSTANCE
# ══════════════════════════════════════════════════════════════════════

_tokenizer_instance = None

def get_tokenizer() -> SinLlamaTokenizer:
    """
    Get global SinLlama tokenizer instance (singleton pattern)
    
    Returns:
        SinLlamaTokenizer instance
    """
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = SinLlamaTokenizer()
    return _tokenizer_instance


# ══════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SINLLAMA TOKENIZER DEMONSTRATION")
    print("=" * 80)
    
    # Initialize tokenizer
    tokenizer = get_tokenizer()
    
    # Test Sinhala text
    sinhala_text = "ශ්‍රී ලංකාව දකුණු ආසියාවේ පිහිටි සුන්දර දිවයින රටකි. මෙහි ජනතාව ඉතා මිත්‍රශීලී වේ."
    
    print("\n1. BASIC TOKENIZATION")
    print("-" * 80)
    stats = tokenizer.analyze_tokenization(sinhala_text)
    print(f"Text: {stats['text']}")
    print(f"Characters: {stats['text_length']}")
    print(f"Tokens: {stats['num_tokens']}")
    print(f"Compression: {stats['compression_ratio']:.2f} chars/token")
    print(f"First 10 tokens: {stats['tokens'][:10]}")
    
    # Test document chunking
    print("\n2. DOCUMENT CHUNKING (for RAG)")
    print("-" * 80)
    long_text = sinhala_text * 5  # Simulate longer document
    chunks = tokenizer.chunk_document(long_text, chunk_size=50, chunk_overlap=10)
    print(f"Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"  Tokens: {chunk['num_tokens']}")
        print(f"  Text: {chunk['text'][:80]}...")
    
    # Test context preparation
    print("\n3. CONTEXT PREPARATION (for generation)")
    print("-" * 80)
    query = "ශ්‍රී ලංකාව පිළිබඳ කියන්න"
    context_chunks = [chunk['text'] for chunk in chunks]
    
    prepared = tokenizer.prepare_context_for_generation(
        query=query,
        retrieved_chunks=context_chunks,
        max_context_tokens=2048
    )
    
    print(f"Query: {prepared['query']}")
    print(f"Chunks used: {prepared['chunks_used']} / {prepared['chunks_available']}")
    print(f"Prompt tokens: {prepared['prompt_tokens']}")
    print(f"Context tokens: {prepared['context_tokens']}")
    print(f"Remaining: {prepared['tokens_remaining']}")
    print(f"Within limit: {prepared['within_limit']}")
    
    print("\n" + "=" * 80)
    print("✅ TOKENIZER READY FOR RAG SYSTEM!")
    print("=" * 80 + "\n")
