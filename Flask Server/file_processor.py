import os
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document
from typing import List, Dict
from llm_service import LLMService

class FileProcessor:
    def __init__(self):
        self.llm_service = LLMService()
    
    def process_file(self, file_path: str, filename: str) -> List[Dict]:
        """
        Process a file and return document chunks
        Returns: [{"text": "content", "metadata": {...}}]
        """
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension == '.txt':
            return self._process_text(file_path, filename)
        elif file_extension == '.pdf':
            return self._process_pdf(file_path, filename)
        elif file_extension == '.docx':
            return self._process_docx(file_path, filename)
        elif file_extension == '.md':
            return self._process_markdown(file_path, filename)
        elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            return self._process_image(file_path, filename)
        else:
            return [{"text": f"Unsupported file type: {file_extension}", "metadata": {"filename": filename, "type": "error"}}]
    
    def _process_text(self, file_path: str, filename: str) -> List[Dict]:
        """Process plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [{
                "text": content,
                "metadata": {
                    "filename": filename,
                    "type": "text",
                    "size": len(content)
                }
            }]
        except Exception as e:
            return [{"text": f"Error processing text file: {str(e)}", "metadata": {"filename": filename, "type": "error"}}]
    
    def _process_pdf(self, file_path: str, filename: str) -> List[Dict]:
        """Process PDF file"""
        try:
            documents = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        documents.append({
                            "text": text,
                            "metadata": {
                                "filename": filename,
                                "type": "pdf",
                                "page": page_num + 1,
                                "total_pages": len(pdf_reader.pages)
                            }
                        })
            
            return documents if documents else [{"text": "PDF contains no extractable text", "metadata": {"filename": filename, "type": "error"}}]
        except Exception as e:
            return [{"text": f"Error processing PDF: {str(e)}", "metadata": {"filename": filename, "type": "error"}}]
    
    def _process_docx(self, file_path: str, filename: str) -> List[Dict]:
        """Process DOCX file"""
        try:
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            content = '\n\n'.join(paragraphs)
            
            return [{
                "text": content,
                "metadata": {
                    "filename": filename,
                    "type": "docx",
                    "paragraphs": len(paragraphs)
                }
            }]
        except Exception as e:
            return [{"text": f"Error processing DOCX: {str(e)}", "metadata": {"filename": filename, "type": "error"}}]
    
    def _process_markdown(self, file_path: str, filename: str) -> List[Dict]:
        """Process Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [{
                "text": content,
                "metadata": {
                    "filename": filename,
                    "type": "markdown",
                    "size": len(content)
                }
            }]
        except Exception as e:
            return [{"text": f"Error processing Markdown: {str(e)}", "metadata": {"filename": filename, "type": "error"}}]
    
    def _process_image(self, file_path: str, filename: str) -> List[Dict]:
        """Process image file - extract text via OCR and generate description"""
        try:
            documents = []
            
            # OCR to extract text
            try:
                image = Image.open(file_path)
                ocr_text = pytesseract.image_to_string(image)
                
                if ocr_text.strip():
                    documents.append({
                        "text": f"OCR Text from {filename}:\n{ocr_text}",
                        "metadata": {
                            "filename": filename,
                            "type": "image_ocr",
                            "image_type": "ocr"
                        }
                    })
            except Exception as ocr_error:
                print(f"OCR failed for {filename}: {ocr_error}")
            
            # Generate visual description using GPT-4 Vision
            try:
                description = self.llm_service.generate_image_description(file_path)
                documents.append({
                    "text": f"Visual Description of {filename}:\n{description}",
                    "metadata": {
                        "filename": filename,
                        "type": "image_description",
                        "image_type": "description"
                    }
                })
            except Exception as desc_error:
                print(f"Description generation failed for {filename}: {desc_error}")
            
            return documents if documents else [{
                "text": f"Image processed: {filename} (no text extracted)",
                "metadata": {"filename": filename, "type": "image", "image_type": "placeholder"}
            }]
        except Exception as e:
            return [{"text": f"Error processing image: {str(e)}", "metadata": {"filename": filename, "type": "error"}}]

