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
    
    def __init__(self, db: Session):
        self.db = db
        self.ollama_url = OLLAMA_BASE_URL
        self.embedding_model = OLLAMA_EMBEDDING_MODEL
        self.embedding_dim = 768  # nomic-embed-text produces 768-dimensional vectors
        self._check_ollama()
        
    def _check_ollama(self):
        """Check if Ollama service is available"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=2
            )
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                print(f"✅ Ollama available with models: {models}")
        except Exception as e:
            print(f"⚠️  Ollama service unavailable: {e}")
    
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
                timeout=60
            )
            
            if response.status_code == 200:
                embeddings = response.json().get('embeddings', [[]])
                if embeddings and len(embeddings) > 0:
                    return embeddings[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return None
    
    def generate_embeddings_batch(self, texts):
        """Generate embeddings for multiple texts"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embed",
                json={
                    "model": self.embedding_model,
                    "input": texts
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get('embeddings', [])
            
            return [None] * len(texts)
            
        except Exception as e:
            print(f"❌ Batch embedding error: {e}")
            return [None] * len(texts)
    
    def add_document_embeddings(self, service_id, document_id, chunks):
        """
        Add document chunks as embeddings to pgvector
        """
        try:
            if not chunks:
                return False, 0, "No chunks to embed"
            
            # Generate embeddings
            embeddings = self.generate_embeddings_batch(chunks)
            
            if not embeddings or len(embeddings) != len(chunks):
                return False, 0, "Failed to generate embeddings"
            
            # Store in Supabase
            added_count = 0
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding is None:
                    continue
                
                try:
                    doc_embedding = DocumentEmbedding(
                        service_id=service_id,
                        document_id=document_id,
                        chunk_index=idx,
                        content=chunk,
                        embedding=embedding,
                        metadata={"chunk_index": idx}
                    )
                    self.db.add(doc_embedding)
                    added_count += 1
                except Exception as e:
                    continue
            
            self.db.commit()
            print(f"✅ Added {added_count} chunks to vector DB")
            return True, added_count, None
            
        except Exception as e:
            self.db.rollback()
            return False, 0, str(e)
    
    def search_similar_documents(self, service_id, query, limit=5):
        """
        Search for similar documents using pgvector
        """
        try:
            query_embedding = self.generate_embedding(query)
            if query_embedding is None:
                return []
            
            # Use pgvector cosine similarity
            results = self.db.query(
                DocumentEmbedding.id,
                DocumentEmbedding.content,
                DocumentEmbedding.metadata,
                text("1 - (embedding <-> :query_embedding) as similarity")
            ).filter(
                DocumentEmbedding.service_id == service_id
            ).order_by(
                text("embedding <-> :query_embedding")
            ).limit(limit).params(query_embedding=query_embedding).all()
            
            matched_results = []
            for result in results:
                id_, content, metadata, similarity = result
                matched_results.append({
                    'id': id_,
                    'content': content,
                    'metadata': metadata,
                    'similarity': float(similarity)
                })
            
            return matched_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def delete_service_embeddings(self, service_id):
        """Delete all embeddings for a service"""
        try:
            count = self.db.query(DocumentEmbedding).filter(
                DocumentEmbedding.service_id == service_id
            ).delete()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False
    
    def get_status(self):
        """Get vector service status"""
        try:
            embedding_count = self.db.query(DocumentEmbedding).count()
            return {
                'status': 'operational',
                'embedding_count': embedding_count,
                'embedding_model': self.embedding_model,
                'embedding_dimension': self.embedding_dim
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


def get_vector_service(db: Session):
    """Factory function to get vector service instance"""
    return VectorDatabaseService(db)

    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'chromadb')
            os.makedirs(data_dir, exist_ok=True)
            
            # Try to initialize ChromaDB client
            try:
                self.client = chromadb.PersistentClient(
                    path=data_dir,
                    settings=Settings(allow_reset=True, anonymized_telemetry=False)
                )
            except Exception as init_error:
                # If initialization fails due to existing instance, try to reset and retry
                logger.warning(f"ChromaDB initialization failed, attempting reset: {str(init_error)}")
                try:
                    # Try creating client with reset
                    temp_client = chromadb.PersistentClient(path=data_dir)
                    temp_client.reset()
                    self.client = chromadb.PersistentClient(
                        path=data_dir,
                        settings=Settings(allow_reset=True, anonymized_telemetry=False)
                    )
                    logger.info("ChromaDB reset and reinitialized successfully")
                except Exception as reset_error:
                    logger.error(f"ChromaDB reset failed: {str(reset_error)}")
                    # Fall back to in-memory client
                    self.client = chromadb.Client()
                    logger.info("Using in-memory ChromaDB client as fallback")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="marketmatic_knowledge_base",
                metadata={"description": "MarketMatic business knowledge for semantic search"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self.client = None
            self.collection = None
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get current status of vector database"""
        try:
            if not self.collection:
                return {
                    'status': 'error',
                    'message': 'Vector database not initialized',
                    'document_count': 0,
                    'modal_status': 'unknown'
                }
            
            # Get collection stats
            count = self.collection.count()
            
            # Check Ollama service status
            ollama_status = 'available' if self.ollama_service.check_service_available() else 'unavailable'
            
            return {
                'status': 'active',
                'message': f'Vector database operational with {count} documents',
                'document_count': count,
                'ai_service': 'ollama-llama3',
                'ollama_status': ollama_status,
                'supported_languages': self.supported_languages,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting database status: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'document_count': 0,
                'ollama_status': 'unknown'
            }
    
    def _process_faqs_for_vectors(self, faqs: List[Dict], service_id: str) -> Tuple[List[str], List[Dict]]:
        """
        Process FAQs into vector-searchable chunks
        
        Args:
            faqs: List of FAQ documents
            service_id: Service identifier
            
        Returns:
            tuple: (chunks, metadata_list)
        """
        chunks = []
        metadata_list = []
        
        for faq in faqs:
            question = faq.get('question', '').strip()
            answer = faq.get('answer', '').strip()
            language = faq.get('language', 'en')
            category = faq.get('category', 'general')
            
            if not question or not answer:
                continue
            
            # Create searchable text combining question and answer
            searchable_text = f"Q: {question}\nA: {answer}"
            
            chunks.append(searchable_text)
            metadata_list.append({
                'type': 'faq',
                'service_id': service_id,
                'question': question,
                'answer': answer,
                'language': language,
                'category': category,
                'faq_id': str(faq.get('_id', '')),
                'created_at': datetime.now().isoformat()
            })
        
        logger.info(f"Processed {len(chunks)} FAQ documents for service {service_id}")
        return chunks, metadata_list
    
    def _process_products_for_vectors(self, products: List[Dict], service_id: str) -> Tuple[List[str], List[Dict]]:
        """
        Process products into vector-searchable chunks
        
        Args:
            products: List of product documents
            service_id: Service identifier
            
        Returns:
            tuple: (chunks, metadata_list)
        """
        chunks = []
        metadata_list = []
        
        for product in products:
            name = product.get('name', '').strip()
            description = product.get('description', '').strip()
            category = product.get('category', 'general')
            price = product.get('price', 0)
            language = product.get('language', 'en')
            
            if not name:
                continue
            
            # Create searchable text
            searchable_text = f"Product: {name}"
            if description:
                searchable_text += f"\nDescription: {description}"
            if price:
                searchable_text += f"\nPrice: {price}"
            if category:
                searchable_text += f"\nCategory: {category}"
            
            chunks.append(searchable_text)
            metadata_list.append({
                'type': 'product',
                'service_id': service_id,
                'name': name,
                'description': description,
                'category': category,
                'price': price,
                'language': language,
                'product_id': str(product.get('_id', '')),
                'created_at': datetime.now().isoformat()
            })
        
        logger.info(f"Processed {len(chunks)} product documents for service {service_id}")
        return chunks, metadata_list
    
    def _process_policies_for_vectors(self, policies: List[Dict], service_id: str) -> Tuple[List[str], List[Dict]]:
        """
        Process policies into vector-searchable chunks
        
        Args:
            policies: List of policy documents
            service_id: Service identifier
            
        Returns:
            tuple: (chunks, metadata_list)
        """
        chunks = []
        metadata_list = []
        
        for policy in policies:
            title = policy.get('title', '').strip()
            content = policy.get('content', '').strip()
            category = policy.get('category', 'general')
            language = policy.get('language', 'en')
            
            if not title or not content:
                continue
            
            # Create searchable text
            searchable_text = f"Policy: {title}\nContent: {content}"
            
            chunks.append(searchable_text)
            metadata_list.append({
                'type': 'policy',
                'service_id': service_id,
                'title': title,
                'content': content,
                'category': category,
                'language': language,
                'policy_id': str(policy.get('_id', '')),
                'created_at': datetime.now().isoformat()
            })
        
        logger.info(f"Processed {len(chunks)} policy documents for service {service_id}")
        return chunks, metadata_list
    
    def semantic_search(
        self, 
        query: str, 
        service_id: str,
        intent: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Perform semantic search across business data
        
        Args:
            query: Search query
            service_id: Service identifier
            intent: Optional intent to filter results
            language: Optional language preference  
            limit: Maximum number of results
            
        Returns:
            Search results with metadata
        """
        try:
            if not self.collection:
                return {
                    'success': False,
                    'message': 'Vector database not initialized',
                    'results': [],
                    'fallback_used': True
                }
            
            # Generate embedding for query using Ollama with nomic-embed-text
            try:
                query_embedding = self.ollama_service.generate_embedding(query)
                if not query_embedding or len(query_embedding) == 0:
                    raise Exception("Ollama returned empty embedding")
                
            except Exception as e:
                logger.error(f"Error generating embedding with Ollama: {str(e)}")
                return {
                    'success': False,
                    'message': 'Embedding generation failed. Make sure Ollama is running.',
                    'results': [],
                    'fallback_used': False
                }
            
            # Build where clause for filtering
            where_clause = {'service_id': service_id}
            if language:
                where_clause['language'] = language
            if intent:
                where_clause['type'] = self._map_intent_to_type(intent)
            
            # Perform vector search
            search_results = self.collection.query(
                query_embeddings=[query_embedding],
                where=where_clause,
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process and format results
            formatted_results = []
            if search_results['documents'] and search_results['documents'][0]:
                for i, doc in enumerate(search_results['documents'][0]):
                    metadata = search_results['metadatas'][0][i] if search_results['metadatas'][0] else {}
                    distance = search_results['distances'][0][i] if search_results['distances'][0] else 1.0
                    
                    # Calculate similarity score (higher is better)
                    similarity = max(0, 1 - distance)
                    
                    formatted_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'distance': distance
                    })
            
            # Apply intent-based filtering if specified
            if intent and formatted_results:
                formatted_results = self._filter_results_by_intent(formatted_results, intent)
            
            return {
                'success': True,
                'message': f'Found {len(formatted_results)} relevant results',
                'results': formatted_results,
                'query': query,
                'intent': intent,
                'language': language,
                'fallback_used': False
            }
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'results': [],
                'fallback_used': True
            }
    
    def _map_intent_to_type(self, intent: str) -> Optional[str]:
        """Map user intent to document type"""
        intent_type_mapping = {
            'product_inquiry': 'product',
            'pricing': 'product',
            'order_tracking': 'policy',
            'delivery': 'policy',
            'complaints': 'policy',
            'general': None  # Search all types
        }
        return intent_type_mapping.get(intent)
    
    def _filter_results_by_intent(self, results: List[Dict], intent: str) -> List[Dict]:
        """Filter search results based on user intent"""
        if not intent or intent not in self.intent_keywords:
            return results
        
        intent_keywords = self.intent_keywords[intent]
        filtered_results = []
        
        for result in results:
            content = result['content'].lower()
            metadata = result['metadata']
            
            # Check if content contains intent-related keywords
            keyword_score = sum(1 for keyword in intent_keywords if keyword in content)
            
            # Boost results that match intent keywords
            if keyword_score > 0:
                result['intent_relevance'] = keyword_score / len(intent_keywords)
                result['similarity'] += result['intent_relevance'] * 0.1  # Small boost
                filtered_results.append(result)
            elif result['similarity'] > 0.7:  # Keep high-similarity results regardless
                result['intent_relevance'] = 0
                filtered_results.append(result)
        
        # Sort by similarity (including intent boost)
        return sorted(filtered_results, key=lambda x: x['similarity'], reverse=True)
    
    def sync_business_data_to_vectors(self, service_id: str, business_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Sync business data (FAQs, products, policies) to vector database
        
        Args:
            service_id: Service identifier
            business_data: Dictionary containing 'faqs', 'products', 'policies'
            
        Returns:
            Sync operation results
        """
        try:
            if not self.collection:
                return {
                    'success': False,
                    'message': 'Vector database not initialized',
                    'details': {}
                }
            
            # Clear existing data for this service
            try:
                self.collection.delete(where={'service_id': service_id})
                logger.info(f"Cleared existing vectors for service {service_id}")
            except Exception as e:
                logger.warning(f"Error clearing existing data: {str(e)}")
            
            total_processed = 0
            all_chunks = []
            all_metadata = []
            all_ids = []
            
            # Process FAQs
            if 'faqs' in business_data and business_data['faqs']:
                faq_chunks, faq_metadata = self._process_faqs_for_vectors(
                    business_data['faqs'], service_id
                )
                all_chunks.extend(faq_chunks)
                all_metadata.extend(faq_metadata)
                # Generate unique IDs for FAQs
                for i, _ in enumerate(faq_chunks):
                    all_ids.append(f"faq_{service_id}_{total_processed + i}")
                total_processed += len(faq_chunks)
            
            # Process Products
            if 'products' in business_data and business_data['products']:
                product_chunks, product_metadata = self._process_products_for_vectors(
                    business_data['products'], service_id
                )
                all_chunks.extend(product_chunks)
                all_metadata.extend(product_metadata)
                # Generate unique IDs for products
                for i, _ in enumerate(product_chunks):
                    all_ids.append(f"product_{service_id}_{total_processed + i}")
                total_processed += len(product_chunks)
            
            # Process Policies
            if 'policies' in business_data and business_data['policies']:
                policy_chunks, policy_metadata = self._process_policies_for_vectors(
                    business_data['policies'], service_id
                )
                all_chunks.extend(policy_chunks)
                all_metadata.extend(policy_metadata)
                # Generate unique IDs for policies
                for i, _ in enumerate(policy_chunks):
                    all_ids.append(f"policy_{service_id}_{total_processed + i}")
                total_processed += len(policy_chunks)
            
            if not all_chunks:
                return {
                    'success': True,
                    'message': 'No data to sync',
                    'details': {
                        'faqs_processed': 0,
                        'products_processed': 0,
                        'policies_processed': 0,
                        'total_chunks': 0
                    }
                }
            
            # Generate embeddings for all chunks using Ollama with nomic-embed-text
            embeddings = []
            batch_size = 10  # Process in smaller batches
            
            for i in range(0, len(all_chunks), batch_size):
                batch_chunks = all_chunks[i:i + batch_size]
                batch_embeddings = []
                
                for chunk in batch_chunks:
                    try:
                        embedding = self.ollama_service.generate_embedding(chunk)
                        if embedding and len(embedding) > 0:
                            batch_embeddings.append(embedding)
                        else:
                            logger.warning(f"Ollama returned empty embedding, using zero vector")
                            batch_embeddings.append([0.0] * 768)  # nomic-embed-text is 768 dims
                    except Exception as e:
                        logger.error(f"Error generating embedding for chunk: {str(e)}")
                        batch_embeddings.append([0.0] * 768)
                
                embeddings.extend(batch_embeddings)
                logger.info(f"✅ Generated embeddings for batch {i//batch_size + 1} using Ollama")
            
            # Add to ChromaDB
            self.collection.add(
                documents=all_chunks,
                metadatas=all_metadata,
                embeddings=embeddings,
                ids=all_ids
            )
            
            # Count documents by type
            faq_count = len([m for m in all_metadata if m['type'] == 'faq'])
            product_count = len([m for m in all_metadata if m['type'] == 'product'])
            policy_count = len([m for m in all_metadata if m['type'] == 'policy'])
            
            logger.info(f"Successfully synced {total_processed} documents to vector database")
            
            return {
                'success': True,
                'message': f'Successfully synced {total_processed} documents',
                'details': {
                    'faqs_processed': faq_count,
                    'products_processed': product_count,
                    'policies_processed': policy_count,
                    'total_chunks': len(all_chunks),
                    'service_id': service_id,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error syncing business data to vectors: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'details': {}
            }
    
    def clear_service_vectors(self, service_id: str) -> Dict[str, Any]:
        """Clear all vectors for a specific service"""
        try:
            if not self.collection:
                return {
                    'success': False,
                    'message': 'Vector database not initialized'
                }
            
            # Count documents before deletion
            count_before = self.collection.count()
            
            # Delete service vectors
            self.collection.delete(where={'service_id': service_id})
            
            # Count documents after deletion
            count_after = self.collection.count()
            deleted_count = count_before - count_after
            
            logger.info(f"Cleared {deleted_count} vectors for service {service_id}")
            
            return {
                'success': True,
                'message': f'Cleared {deleted_count} vectors for service {service_id}',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            logger.error(f"Error clearing service vectors: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'deleted_count': 0
            }
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get statistics about stored vectors"""
        try:
            if not self.collection:
                return {
                    'success': False,
                    'message': 'Vector database not initialized',
                    'stats': {}
                }
            
            total_count = self.collection.count()
            
            # Get sample of metadata to analyze distribution
            if total_count > 0:
                sample_results = self.collection.get(limit=min(100, total_count))
                metadatas = sample_results.get('metadatas', [])
                
                # Analyze distribution
                type_counts = {}
                service_counts = {}
                language_counts = {}
                
                for metadata in metadatas:
                    doc_type = metadata.get('type', 'unknown')
                    service_id = metadata.get('service_id', 'unknown')
                    language = metadata.get('language', 'unknown')
                    
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                    service_counts[service_id] = service_counts.get(service_id, 0) + 1
                    language_counts[language] = language_counts.get(language, 0) + 1
                
                stats = {
                    'total_documents': total_count,
                    'type_distribution': type_counts,
                    'service_distribution': service_counts,
                    'language_distribution': language_counts,
                    'sample_size': len(metadatas)
                }
            else:
                stats = {
                    'total_documents': 0,
                    'type_distribution': {},
                    'service_distribution': {},
                    'language_distribution': {},
                    'sample_size': 0
                }
            
            return {
                'success': True,
                'message': 'Vector statistics retrieved successfully',
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting vector stats: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'stats': {}
            }
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text using Ollama with nomic-embed-text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        try:
            embedding = self.ollama_service.generate_embedding(text)
            if embedding and len(embedding) > 0:
                return embedding
            else:
                logger.error("Ollama returned empty embedding")
                return None
        except Exception as e:
            logger.error(f"Error generating embedding with Ollama: {str(e)}")
            return None

    def add_documents(self, service_id: str, chunks: List[str], metadata: Dict = None) -> int:
        """
        Add documents to the vector database
        
        Args:
            service_id: Service ID to associate documents with
            chunks: List of text chunks to add
            metadata: Optional metadata for documents
            
        Returns:
            Number of documents added
        """
        if not self.collection:
            logger.error("ChromaDB collection not initialized")
            return 0
            
        try:
            # Generate embeddings for chunks
            embeddings = []
            valid_chunks = []
            
            for chunk in chunks:
                if chunk and chunk.strip():
                    embedding = self.get_embedding(chunk.strip())
                    if embedding:
                        embeddings.append(embedding)
                        valid_chunks.append(chunk.strip())
            
            if not embeddings:
                logger.warning("No valid embeddings generated")
                return 0
            
            # Prepare documents for insertion
            doc_ids = []
            metadatas = []
            
            base_metadata = {
                'service_id': service_id,
                'type': 'document',
                'added_at': datetime.now().isoformat()
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            for i in range(len(valid_chunks)):
                doc_id = f"{service_id}_doc_{hash(valid_chunks[i])}_{i}"
                doc_ids.append(doc_id)
                metadatas.append(base_metadata.copy())
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=valid_chunks,
                metadatas=metadatas,
                ids=doc_ids
            )
            
            logger.info(f"Added {len(valid_chunks)} documents for service {service_id}")
            return len(valid_chunks)
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return 0


# Global service instance
_vector_service = None

def get_vector_service() -> VectorDatabaseService:
    """Get or create the global vector database service instance"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorDatabaseService()
    return _vector_service