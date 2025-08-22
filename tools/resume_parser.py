"""Resume Parser Tool for extracting text from various resume formats."""

import re
from pathlib import Path
from typing import Dict, Any, Optional


class ResumeParser:
    """Tool for parsing resumes and extracting text content."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.md', '.docx']
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse a resume file and extract text content."""
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "text": "",
                "file_type": path.suffix.lower()
            }
        
        file_type = path.suffix.lower()
        
        if file_type not in self.supported_formats:
            return {
                "success": False,
                "error": f"Unsupported file format: {file_type}",
                "text": "",
                "file_type": file_type
            }
        
        try:
            if file_type == '.pdf':
                text = self._extract_pdf_text(path)
            elif file_type == '.docx':
                text = self._extract_docx_text(path)
            else:
                text = self._extract_text_file(path)
            
            return {
                "success": True,
                "text": text,
                "file_type": file_type,
                "text_length": len(text),
                "extracted_info": self._extract_basic_info(text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "file_type": file_type
            }
    
    def _extract_pdf_text(self, path: Path) -> str:
        """Extract text from PDF files."""
        try:
            import PyPDF2
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return text
            except ImportError:
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(path)
                    text = ""
                    for page in doc:
                        text += page.get_text() + "\n"
                    doc.close()
                    return text
                except ImportError:
                    raise Exception("No PDF parsing library available. Install PyPDF2, pdfplumber, or PyMuPDF.")
    
    def _extract_docx_text(self, path: Path) -> str:
        """Extract text from DOCX files."""
        try:
            from docx import Document
            doc = Document(path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise Exception("python-docx library not available. Install with: pip install python-docx")
    
    def _extract_text_file(self, path: Path) -> str:
        """Extract text from text-based files."""
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding='latin-1')
            except Exception as e:
                raise Exception(f"Could not read text file: {str(e)}")
    
    def _extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract basic information from resume text."""
        info = {
            "emails": [],
            "phones": [],
            "github_links": [],
            "linkedin_links": [],
            "urls": []
        }
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        info["emails"] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}'
        info["phones"] = re.findall(phone_pattern, text)
        
        # Extract GitHub links
        github_pattern = r'https?://github\.com/[^\s\)]+'
        info["github_links"] = re.findall(github_pattern, text)
        
        # Extract LinkedIn links
        linkedin_pattern = r'https?://linkedin\.com/[^\s\)]+'
        info["linkedin_links"] = re.findall(linkedin_pattern, text)
        
        # Extract other URLs
        url_pattern = r'https?://[^\s\)]+'
        info["urls"] = re.findall(url_pattern, text)
        
        return info

