import os
import re
import pandas as pd
from io import BytesIO
from pypdf import PdfReader
from docx import Document as DocxDocument
import openpyxl

class DocumentProcessor:
    """Service for processing various document types and extracting text"""
    
    @staticmethod
    def chunk_text(text, chunk_size=600, chunk_overlap=100):
        """
        Split text into overlapping chunks for better context preservation
        OPTIMIZED for multi-business RAG system
        
        Args:
            text: The text to chunk
            chunk_size: Maximum characters per chunk (increased for better context)
            chunk_overlap: Number of characters to overlap between chunks
        
        Returns:
            List of text chunks
        """
        if not text or len(text) == 0:
            return []
        
        # Clean the text - preserve structure
        text = re.sub(r'\s+', ' ', text).strip()
        
        # If text is very short, return as single chunk
        if len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + chunk_size, len(text))
            
            # If not the last chunk, try to break at natural boundaries
            if end < len(text):
                # Look for sentence endings (., !, ?, \n) near the chunk boundary
                best_break = -1
                search_start = max(start + chunk_size - 150, start + chunk_size // 2)
                
                for i in range(end, search_start, -1):
                    if i < len(text) and text[i] in '.!?\n':
                        best_break = i + 1
                        break
                
                # If found a good break point, use it
                if best_break > 0:
                    end = best_break
                # Otherwise, try to break at word boundary
                elif end < len(text):
                    for i in range(end, max(start + chunk_size - 50, start), -1):
                        if i < len(text) and text[i].isspace():
                            end = i
                            break
            
            chunk = text[start:end].strip()
            if chunk and len(chunk) > 20:  # Only add chunks with meaningful content
                chunks.append(chunk)
            
            # Move start position with overlap to maintain context
            start = end - chunk_overlap
            
            # Safety check to prevent infinite loop
            if start >= len(text) or (len(chunks) > 0 and start <= chunks.__len__() * (chunk_size - chunk_overlap) - chunk_size):
                break
        
        print(f"[CHUNKING] Created {len(chunks)} chunks from {len(text)} chars (avg: {len(text)//max(len(chunks),1)} chars/chunk)")
        return chunks
    
    @staticmethod
    def process_pdf(file_content):
        """
        Extract text from PDF file
        
        Args:
            file_content: Binary content of PDF file
        
        Returns:
            Extracted text as string
        """
        try:
            pdf_file = BytesIO(file_content)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def process_excel(file_content):
        """
        Extract data from Excel file and convert to text
        
        Args:
            file_content: Binary content of Excel file
        
        Returns:
            Formatted text representation of Excel data
        """
        try:
            excel_file = BytesIO(file_content)
            
            # Try to read with pandas first (handles both .xls and .xlsx)
            df = pd.read_excel(excel_file, sheet_name=None)  # Read all sheets
            
            text = ""
            for sheet_name, sheet_df in df.items():
                text += f"=== Sheet: {sheet_name} ===\n\n"
                
                # Convert dataframe to readable text format
                # Include column headers
                headers = " | ".join(str(col) for col in sheet_df.columns)
                text += headers + "\n"
                text += "-" * len(headers) + "\n"
                
                # Add each row
                for idx, row in sheet_df.iterrows():
                    row_text = " | ".join(str(val) if pd.notna(val) else "" for val in row)
                    text += row_text + "\n"
                
                text += "\n\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error processing Excel: {str(e)}")
    
    @staticmethod
    def process_word(file_content):
        """
        Extract text from Word document
        
        Args:
            file_content: Binary content of Word file
        
        Returns:
            Extracted text as string
        """
        try:
            doc_file = BytesIO(file_content)
            doc = DocxDocument(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n\n"
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    text += row_text + "\n"
                text += "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error processing Word document: {str(e)}")
    
    @staticmethod
    def process_text(file_content):
        """
        Process plain text file
        
        Args:
            file_content: Binary content of text file
        
        Returns:
            Decoded text as string
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    text = file_content.decode(encoding)
                    return text.strip()
                except UnicodeDecodeError:
                    continue
            
            # If all fail, use utf-8 with error handling
            return file_content.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")
    
    @staticmethod
    def process_faq(faq_data):
        """
        Process FAQ data into text format
        
        Args:
            faq_data: List of FAQ objects with question and answer
        
        Returns:
            Formatted FAQ text
        """
        text = "=== Frequently Asked Questions ===\n\n"
        
        for idx, faq in enumerate(faq_data, 1):
            question = faq.get('question', {})
            answer = faq.get('answer', {})
            category = faq.get('category', 'General')
            
            text += f"FAQ #{idx} [Category: {category}]\n"
            
            # English
            if question.get('en'):
                text += f"Q (English): {question['en']}\n"
            if answer.get('en'):
                text += f"A (English): {answer['en']}\n"
            
            # Sinhala
            if question.get('si'):
                text += f"Q (Sinhala): {question['si']}\n"
            if answer.get('si'):
                text += f"A (Sinhala): {answer['si']}\n"
            
            text += "\n" + "-" * 50 + "\n\n"
        
        return text.strip()
    
    @staticmethod
    def process_products(product_data):
        """
        Process product data into text format
        
        Args:
            product_data: List of product objects
        
        Returns:
            Formatted product text
        """
        text = "=== Product Catalog ===\n\n"
        
        for product in product_data:
            name = product.get('name', {})
            description = product.get('description', {})
            price = product.get('price', 0)
            stock = product.get('stock', 0)
            category = product.get('category', 'General')
            sku = product.get('sku', 'N/A')
            
            text += f"Product: {name.get('en', name.get('si', 'Unknown'))}\n"
            text += f"SKU: {sku}\n"
            text += f"Category: {category}\n"
            text += f"Price: Rs. {price}\n"
            text += f"Stock: {stock} units\n"
            
            # Descriptions
            if description.get('en'):
                text += f"Description (English): {description['en']}\n"
            if description.get('si'):
                text += f"Description (Sinhala): {description['si']}\n"
            
            text += "\n" + "-" * 50 + "\n\n"
        
        return text.strip()
    
    @staticmethod
    def process_policies(policy_data):
        """
        Process policy documents into text format
        
        Args:
            policy_data: List of policy objects
        
        Returns:
            Formatted policy text
        """
        text = "=== Shop Policies ===\n\n"
        
        for policy in policy_data:
            title = policy.get('title', {})
            content = policy.get('content', {})
            
            # English
            if title.get('en'):
                text += f"=== {title['en']} ===\n\n"
                if content.get('en'):
                    text += f"{content['en']}\n\n"
            
            # Sinhala
            if title.get('si'):
                text += f"=== {title['si']} ===\n\n"
                if content.get('si'):
                    text += f"{content['si']}\n\n"
            
            text += "-" * 50 + "\n\n"
        
        return text.strip()
    
    @staticmethod
    def extract_metadata(filename, file_type, content):
        """
        Extract metadata from document
        
        Args:
            filename: Name of the file
            file_type: Type of file
            content: Extracted text content
        
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'filename': filename,
            'file_type': file_type,
            'char_count': len(content),
            'word_count': len(content.split()),
            'has_sinhala': bool(re.search(r'[\u0D80-\u0DFF]', content)),
            'has_english': bool(re.search(r'[a-zA-Z]', content))
        }
        
        return metadata
