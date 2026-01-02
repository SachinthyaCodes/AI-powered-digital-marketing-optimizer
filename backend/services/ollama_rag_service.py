"""
Integrated RAG Service using Ollama for Local Inference (English Only)
Connects with bot management for FAQ/document processing
Uses Ollama for embedding & generation locally
"""
import os
import json
from typing import List, Dict, Optional
import requests
from datetime import datetime

# Import Ollama RAG system
from services.ollama_rag_system import OllamaRAGSystem
from services.document_processor import DocumentProcessor
from services.ollama_service import OllamaService
from database import SessionLocal
from models.sqlalchemy_models import Document, FAQ


class OllamaRAGService:
    """
    RAG Service that uses Ollama for local inference (English only)
    Handles document processing, embedding, and generation via Ollama
    """
    
    def __init__(self, service_id: str):
        """
        Initialize Ollama RAG service for a specific service/business
        
        Args:
            service_id: Service UUID
        """
        self.service_id = service_id
        self.document_processor = DocumentProcessor()
        
        # Initialize Ollama service
        self.ollama_service = OllamaService()
        
        # Initialize RAG system for this service
        self.rag_system = OllamaRAGSystem(
            chunk_size=500,
            chunk_overlap=50,
            max_context_tokens=4096,
            vector_db_path=os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'rag_indices',
                f'service_{service_id}'
            )
        )
        
        # Try to load existing index
        try:
            index_path = self.rag_system.vector_db_path
            if os.path.exists(f"{index_path}.json"):
                self.rag_system.load_index()
                print(f"✅ Loaded RAG index for service {service_id[:8]}")
        except Exception as e:
            print(f"⚠️ No existing index: {e}")
    
    # ══════════════════════════════════════════════════════════════════
    # DOCUMENT PROCESSING (For Bot Management)
    # ══════════════════════════════════════════════════════════════════
    
    def process_document_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Process uploaded document file (PDF, DOCX, TXT, etc.)
        
        Args:
            file_content: Binary file content
            filename: Original filename
        
        Returns:
            Processing result with extracted text and chunks
        """
        try:
            # Extract text based on file type
            file_ext = filename.rsplit('.', 1)[-1].lower()
            
            if file_ext == 'pdf':
                text = self.document_processor.process_pdf(file_content)
            elif file_ext in ['xlsx', 'xls']:
                text = self.document_processor.process_excel(file_content)
            elif file_ext == 'docx':
                text = self.document_processor.process_word(file_content)
            else:  # txt
                text = file_content.decode('utf-8', errors='ignore')
            
            if not text or len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Could not extract text or content too short'
                }
            
            # Chunk the document
            chunks = self.rag_system.chunk_document(text, metadata={
                'filename': filename,
                'document_type': file_ext,
                'service_id': self.service_id,
                'processed_at': datetime.now().isoformat()
            })
            
            # Count total characters
            total_chars = sum(len(chunk['text']) for chunk in chunks)
            
            return {
                'success': True,
                'text': text,
                'chunks': chunks,
                'num_chunks': len(chunks),
                'total_chars': total_chars,
                'filename': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Document processing failed: {str(e)}'
            }
    
    def extract_faqs_from_text(self, text: str) -> List[Dict]:
        """
        Extract Q&A pairs from text using pattern matching
        Supports English only
        
        Args:
            text: Document text
        
        Returns:
            List of extracted FAQs with question/answer
        """
        print(f"[FAQ DEBUG] Text length: {len(text)} characters")
        print(f"[FAQ DEBUG] First 300 chars: {text[:300]}")
        
        faqs = []
        lines = text.split('\n')
        
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with question indicator (English only)
            # More flexible patterns
            if any(line.lower().startswith(prefix) for prefix in [
                'q:', 'question:', 'q.', 'q)', '?', 'faq:', 'query:'
            ]) or (line.endswith('?') and len(line) > 10):
                # Save previous Q&A if exists
                if current_question and current_answer:
                    faqs.append({
                        'question': current_question,
                        'answer': ' '.join(current_answer).strip()
                    })
                
                # Start new question
                current_question = line
                for prefix in ['Q:', 'Question:', 'Q.', 'q:', 'question:', 'q.', 'Q)', 'q)', 'FAQ:', 'faq:', 'Query:', 'query:']:
                    current_question = current_question.replace(prefix, '', 1).strip()
                current_answer = []
                
            # Check if line starts with answer indicator
            elif any(line.lower().startswith(prefix) for prefix in [
                'a:', 'answer:', 'a.', 'a)', 'ans:', 'reply:'
            ]):
                # Start answer
                answer_text = line
                for prefix in ['A:', 'Answer:', 'A.', 'a:', 'answer:', 'a.', 'A)', 'a)', 'Ans:', 'ans:', 'Reply:', 'reply:']:
                    answer_text = answer_text.replace(prefix, '', 1).strip()
                current_answer = [answer_text]
                
            # Continue answer if we have a question
            elif current_question:
                current_answer.append(line)
        
        # Add last Q&A if exists
        if current_question and current_answer:
            faqs.append({
                'question': current_question,
                'answer': ' '.join(current_answer).strip()
            })
        
        print(f"[FAQ DEBUG] Extraction complete: {len(faqs)} FAQs found")
        for i, faq in enumerate(faqs, 1):
            print(f"[FAQ DEBUG]   {i}. Q: {faq['question'][:60]}...")
        
        return faqs
    
    def add_document_to_rag(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Add document to RAG system and save index
        
        Args:
            document_id: Document UUID
            text: Document text
            metadata: Optional metadata
        
        Returns:
            Processing result
        """
        try:
            doc_metadata = metadata or {}
            doc_metadata['document_id'] = document_id
            
            # Add to RAG
            result = self.rag_system.add_documents([{
                'text': text,
                'metadata': doc_metadata
            }])
            
            if result['success']:
                # Save index
                self.rag_system.save_index()
                print(f"✅ Document {document_id[:8]} added to RAG and index saved")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to add document to RAG: {str(e)}'
            }
    
    def query_with_ollama(
        self,
        question: str,
        top_k: int = 5,
        model: str = "llama2"
    ) -> Dict:
        """
        Query RAG system and generate answer using Ollama
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            model: Ollama model to use
        
        Returns:
            Query result with generated answer
        """
        try:
            # Retrieve relevant context
            rag_result = self.rag_system.query(
                question=question,
                top_k=top_k,
                min_similarity=0.3
            )
            
            if not rag_result['success']:
                return {
                    'success': False,
                    'question': question,
                    'answer': 'No relevant information found in the knowledge base.',
                    'sources': []
                }
            
            # Build prompt for Ollama
            context = rag_result['context']
            prompt = f"""You are a helpful assistant. Answer the question based on the provided context.

Context:
{context}

Question: {question}

Answer: Provide a clear and concise answer based on the context above."""

            # Generate answer using Ollama
            try:
                response = self.ollama_service.generate(
                    prompt=prompt,
                    model=model,
                    max_tokens=500
                )
                
                answer = response.get('response', 'Unable to generate answer.')
                
                return {
                    'success': True,
                    'question': question,
                    'answer': answer,
                    'context': context,
                    'sources': rag_result['sources'],
                    'num_sources': rag_result['num_sources'],
                    'model': model
                }
                
            except Exception as ollama_error:
                # Fallback if Ollama fails
                print(f"⚠️ Ollama generation failed: {ollama_error}")
                return {
                    'success': True,
                    'question': question,
                    'answer': f"Based on the available information: {rag_result['sources'][0]['text'][:300]}..." if rag_result['sources'] else "Unable to generate answer.",
                    'sources': rag_result['sources'],
                    'num_sources': rag_result['num_sources'],
                    'model': 'fallback'
                }
                
        except Exception as e:
            return {
                'success': False,
                'question': question,
                'error': str(e)
            }
    
    def rebuild_index_from_database(self):
        """
        Rebuild RAG index from all documents in database for this service
        """
        try:
            db = SessionLocal()
            
            # Get all documents for this service
            documents = db.query(Document).filter(
                Document.service_id == self.service_id
            ).all()
            
            if not documents:
                return {
                    'success': False,
                    'error': 'No documents found for this service'
                }
            
            # Clear existing index
            self.rag_system.clear()
            
            # Add all documents
            docs_to_add = []
            for doc in documents:
                # Read document file
                if doc.file_path and os.path.exists(doc.file_path):
                    with open(doc.file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    docs_to_add.append({
                        'text': text,
                        'metadata': {
                            'document_id': str(doc.id),
                            'filename': doc.filename,
                            'service_id': self.service_id
                        }
                    })
            
            # Add to RAG
            result = self.rag_system.add_documents(docs_to_add)
            
            if result['success']:
                # Save index
                self.rag_system.save_index()
                print(f"✅ Rebuilt index for service {self.service_id[:8]}")
            
            db.close()
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to rebuild index: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """Get RAG service status"""
        return {
            'service_id': self.service_id,
            'num_chunks': len(self.rag_system.chunks),
            'index_exists': self.rag_system.index is not None,
            'embedding_dim': self.rag_system.embedding_dim,
            'ollama_available': self.ollama_service.test_connection()
        }
