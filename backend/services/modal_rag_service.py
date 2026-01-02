"""
Integrated RAG Service using Modal for Remote Inference
Connects with bot management for FAQ/document processing
Uses Modal for embedding & generation (not local PC)
"""
import os
import json
from typing import List, Dict, Optional
import requests
from datetime import datetime

# Import complete RAG system (for vector operations)
from services.complete_rag_system import SinhalaRAGSystem
from services.document_processor import DocumentProcessor
from database import SessionLocal
from models.sqlalchemy_models import Document, FAQ


class ModalRAGService:
    """
    RAG Service that uses Modal for remote inference
    Handles document processing, embedding, and generation via Modal API
    """
    
    def __init__(self, service_id: str):
        """
        Initialize Modal RAG service for a specific service/business
        
        Args:
            service_id: Service UUID
        """
        self.service_id = service_id
        self.document_processor = DocumentProcessor()
        
        # Modal endpoints (configure in .env)
        self.modal_embedding_url = os.getenv('MODAL_EMBEDDING_URL', '')
        self.modal_chat_url = os.getenv('MODAL_CHAT_URL', '')
        self.modal_generate_url = os.getenv('MODAL_GENERATE_URL', '')
        
        # Initialize RAG system for this service
        self.rag_system = SinhalaRAGSystem(
            chunk_size=512,
            chunk_overlap=50,
            max_context_tokens=2048,
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
                'processed_at': datetime.utcnow().isoformat()
            })
            
            return {
                'success': True,
                'text': text,
                'chunks': chunks,
                'chunk_count': len(chunks),
                'total_tokens': sum(c['num_tokens'] for c in chunks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def extract_faqs_from_text(self, text: str) -> List[Dict]:
        """
        Extract FAQ pairs from document text
        Looks for Q&A patterns
        
        Args:
            text: Document text
        
        Returns:
            List of FAQ dictionaries
        """
        faqs = []
        
        # Simple pattern matching for FAQ extraction
        lines = text.split('\n')
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a question
            if any(line.startswith(prefix) for prefix in ['Q:', 'Question:', 'ප්‍රශ්නය:', '?']):
                # Save previous FAQ
                if current_question and current_answer:
                    faqs.append({
                        'question': current_question,
                        'answer': ' '.join(current_answer).strip()
                    })
                
                # Start new question
                current_question = line.replace('Q:', '').replace('Question:', '').replace('ප්‍රශ්නය:', '').strip()
                current_answer = []
            
            # Check if line looks like an answer
            elif any(line.startswith(prefix) for prefix in ['A:', 'Answer:', 'පිළිතුර:', 'උත්තරය:']):
                current_answer = [line.replace('A:', '').replace('Answer:', '').replace('පිළිතුර:', '').replace('උත්තරය:', '').strip()]
            
            # Continue answer
            elif current_question and not any(line.startswith(p) for p in ['Q:', 'Question:', 'ප්‍රශ්නය:']):
                current_answer.append(line)
        
        # Add last FAQ
        if current_question and current_answer:
            faqs.append({
                'question': current_question,
                'answer': ' '.join(current_answer).strip()
            })
        
        return faqs
    
    def add_document_to_rag(
        self,
        document_id: str,
        text: str,
        filename: str,
        extract_faqs: bool = True
    ) -> Dict:
        """
        Add document to RAG system and optionally extract FAQs
        
        Args:
            document_id: Document UUID
            text: Extracted text
            filename: Original filename
            extract_faqs: Whether to extract FAQ pairs
        
        Returns:
            Result with indexing info and FAQs
        """
        try:
            # Add to RAG system
            result = self.rag_system.add_documents(
                documents=[text],
                metadata=[{
                    'doc_id': document_id,
                    'filename': filename,
                    'service_id': self.service_id,
                    'indexed_at': datetime.utcnow().isoformat()
                }]
            )
            
            # Extract FAQs if requested
            faqs = []
            if extract_faqs:
                faqs = self.extract_faqs_from_text(text)
            
            # Save index
            self.rag_system.save_index()
            
            return {
                'success': True,
                'chunks': result.get('num_chunks', 0),
                'tokens': result.get('total_tokens', 0),
                'faqs_extracted': len(faqs),
                'faqs': faqs
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'RAG indexing failed: {str(e)}'
            }
    
    # ══════════════════════════════════════════════════════════════════
    # QUERY WITH MODAL (Remote Generation)
    # ══════════════════════════════════════════════════════════════════
    
    def query_with_modal(
        self,
        question: str,
        top_k: int = 5,
        language: str = 'si',
        use_modal: bool = True
    ) -> Dict:
        """
        Query RAG system and generate answer using Modal
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            language: Response language
            use_modal: Use Modal for generation (True) or local fallback (False)
        
        Returns:
            Complete response with answer and sources
        """
        try:
            # 1. Retrieve relevant chunks
            rag_result = self.rag_system.query(
                question=question,
                top_k=top_k,
                min_score=0.3,
                language=language,
                return_prompt=True
            )
            
            if not rag_result['success']:
                return rag_result
            
            # 2. Generate answer
            if use_modal and self.modal_generate_url:
                # Use Modal for generation
                try:
                    print(f"🚀 Calling Modal for generation...")
                    response = requests.post(
                        self.modal_generate_url,
                        json={
                            'prompt': rag_result['prompt'],
                            'max_tokens': 512,
                            'temperature': 0.7
                        },
                        timeout=60
                    )
                    response.raise_for_status()
                    modal_result = response.json()
                    
                    rag_result['answer'] = modal_result.get('response', modal_result.get('text', ''))
                    rag_result['generation_source'] = 'modal'
                    rag_result['tokens_used'] = modal_result.get('tokens_used', 0)
                    
                    print(f"✅ Modal generation complete")
                    
                except Exception as e:
                    print(f"❌ Modal generation failed: {e}")
                    # Fall back to local if Modal fails
                    rag_result['answer'] = self._fallback_answer(question, rag_result)
                    rag_result['generation_source'] = 'fallback'
                    rag_result['generation_error'] = str(e)
            else:
                # Use fallback (no model generation)
                rag_result['answer'] = self._fallback_answer(question, rag_result)
                rag_result['generation_source'] = 'fallback'
            
            return rag_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'question': question
            }
    
    def _fallback_answer(self, question: str, rag_result: Dict) -> str:
        """Generate fallback answer from retrieved chunks (no LLM)"""
        if not rag_result.get('sources'):
            if 'si' in rag_result.get('language', '').lower():
                return "මට ඔබේ ප්‍රශ්නයට අදාළ තොරතුරු සොයා ගැනීමට නොහැකි විය."
            else:
                return "I couldn't find relevant information for your question."
        
        # Combine top sources
        sources_text = "\n\n".join([
            s['text_preview'] for s in rag_result['sources'][:2]
        ])
        
        if 'si' in rag_result.get('language', '').lower():
            return f"අපගේ ලේඛනවල සඳහන් තොරතුරු අනුව:\n\n{sources_text}"
        else:
            return f"Based on our documents:\n\n{sources_text}"
    
    # ══════════════════════════════════════════════════════════════════
    # STATS & MANAGEMENT
    # ══════════════════════════════════════════════════════════════════
    
    def get_stats(self) -> Dict:
        """Get RAG statistics for this service"""
        return self.rag_system.get_stats()
    
    def rebuild_index(self) -> Dict:
        """Rebuild RAG index from all documents in database"""
        db = SessionLocal()
        try:
            # Get all documents for this service
            documents = db.query(Document).filter(
                Document.service_id == self.service_id
            ).all()
            
            if not documents:
                return {
                    'success': True,
                    'message': 'No documents to index',
                    'count': 0
                }
            
            # Reset and rebuild
            self.rag_system.chunks = []
            self.rag_system.chunk_texts = []
            self.rag_system.metadata_store = []
            self.rag_system.index = None
            
            # Re-index all
            texts = [doc.content for doc in documents if doc.content]
            metadata = [{
                'doc_id': str(doc.id),
                'filename': doc.filename,
                'service_id': self.service_id
            } for doc in documents if doc.content]
            
            result = self.rag_system.add_documents(texts, metadata)
            
            return {
                'success': True,
                'documents': len(documents),
                'chunks': result.get('num_chunks', 0),
                'tokens': result.get('total_tokens', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def get_modal_rag_service(service_id: str) -> ModalRAGService:
    """
    Get or create Modal RAG service instance for a service
    
    Args:
        service_id: Service UUID
    
    Returns:
        ModalRAGService instance
    """
    return ModalRAGService(service_id)
