"""Comprehensive Resume Parser Tool for extracting and structuring resume data."""

import json
import re
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    """Structured resume data extracted by LLM."""
    
    candidate_name: str = Field(description="Full name of the candidate", default="")
    email: str = Field(description="Primary email address", default="")
    phone: str = Field(description="Primary phone number", default="")
    linkedin: str = Field(description="LinkedIn profile URL", default="")
    github: str = Field(description="GitHub profile URL", default="")
    portfolio: str = Field(description="Portfolio website URL", default="")
    
    education: list[Dict[str, Any]] = Field(description="List of education entries", default_factory=list)
    experience: list[Dict[str, Any]] = Field(description="List of work experience entries", default_factory=list)
    skills: Dict[str, list[str]] = Field(description="Skills categorized as primary, secondary, tools", default_factory=lambda: {"primary": [], "secondary": [], "tools": []})
    projects: list[Dict[str, Any]] = Field(description="List of projects", default_factory=list)
    
    other_links: list[str] = Field(description="Other relevant links found in the resume", default_factory=list)
    parse_warnings: list[str] = Field(description="Any warnings or issues during parsing", default_factory=list)
    
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to handle None values."""
        if isinstance(obj, dict):
            # Clean up None values in nested dictionaries
            def clean_none_values(data):
                if isinstance(data, dict):
                    return {k: clean_none_values(v) for k, v in data.items() if v is not None}
                elif isinstance(data, list):
                    return [clean_none_values(item) for item in data if item is not None]
                else:
                    return data
            
            obj = clean_none_values(obj)
        
        return super().model_validate(obj)


class ResumeParser:
    """Comprehensive tool for parsing resumes and extracting structured data."""
    
    def __init__(self, llm_model: str = "google/gemini-2.0-flash"):
        self.llm_model = llm_model
        self.supported_formats = ['.pdf', '.txt', '.md', '.docx']
    
    def parse_resume(self, file_path: str, llm=None) -> Dict[str, Any]:
        """Parse a resume file and extract text content with basic info."""
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
            # Extract text content
            if file_type == '.pdf':
                text = self._extract_pdf_text(path)
            elif file_type == '.docx':
                text = self._extract_docx_text(path)
            else:
                text = self._extract_text_file(path)
            
            # Extract basic information using regex
            basic_info = self._extract_basic_info(text)
            
            return {
                "success": True,
                "text": text,
                "file_type": file_type,
                "text_length": len(text),
                "extracted_info": basic_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "file_type": file_type
            }
    
    def parse_resume_with_llm(self, resume_path: str, llm) -> ResumeData:
        """Parse any resume format using LLM for structured data extraction."""
        if not Path(resume_path).exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        
        # Extract text content from the resume file
        resume_text = self._extract_text(resume_path)
        
        # Use LLM to parse the resume text into structured data
        parsed_data = self._parse_with_llm(resume_text, llm)
        
        return ResumeData(**parsed_data)
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text content from any file format."""
        path = Path(file_path)
        file_extension = path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._extract_pdf_text(path)
        else:
            return self._extract_text_from_file(path)
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from text-based files."""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding='latin-1')
            except Exception as e:
                raise ValueError(f"Could not read file {file_path}: {str(e)}")
    
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF files with multiple fallback methods."""
        print(f"🔍 Attempting to extract text from PDF: {pdf_path}")
        
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                print(f"📄 PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    print(f"📝 Page {page_num + 1}: {len(page_text)} characters")
                    if page_text.strip():  # Only add non-empty pages
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                
                if not text.strip():
                    print("⚠️ PyPDF2 extracted no text, trying alternative methods...")
                    return self._extract_text_alternative_pdf(pdf_path)
                
                print(f"✅ PyPDF2 extracted {len(text)} characters total")
                return text
                
        except ImportError:
            print("⚠️ PyPDF2 not available, trying alternative methods...")
            return self._extract_text_alternative_pdf(pdf_path)
        except Exception as e:
            print(f"❌ PyPDF2 extraction failed: {e}")
            return self._extract_text_alternative_pdf(pdf_path)
    
    def _extract_text_alternative_pdf(self, pdf_path: Path) -> str:
        """Alternative PDF text extraction methods."""
        print("🔄 Trying alternative PDF extraction methods...")
        
        try:
            # Try with pdfplumber if available
            import pdfplumber
            print("📖 Trying pdfplumber...")
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    print(f"📝 Page {page_num + 1}: {len(page_text) if page_text else 0} characters")
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                
                if text.strip():
                    print(f"✅ pdfplumber extracted {len(text)} characters")
                    return text
                else:
                    print("⚠️ pdfplumber extracted no text")
                    
        except ImportError:
            print("⚠️ pdfplumber not available")
        except Exception as e:
            print(f"❌ pdfplumber extraction failed: {e}")
        
        try:
            # Try with pymupdf if available
            import fitz  # PyMuPDF
            print("📖 Trying PyMuPDF...")
            doc = fitz.open(pdf_path)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                print(f"📝 Page {page_num + 1}: {len(page_text) if page_text else 0} characters")
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text + "\n"
            doc.close()
            
            if text.strip():
                print(f"✅ PyMuPDF extracted {len(text)} characters")
                return text
            else:
                print("⚠️ PyMuPDF extracted no text")
                
        except ImportError:
            print("⚠️ PyMuPDF not available")
        except Exception as e:
            print(f"❌ PyMuPDF extraction failed: {e}")
        
        # Try basic file reading as last resort
        try:
            print("📖 Trying basic file reading...")
            with open(pdf_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📝 Basic reading: {len(content)} characters")
                if content.strip():
                    return content
        except Exception as e:
            print(f"❌ Basic file reading failed: {e}")
        
        # Final fallback - return a message indicating OCR is needed
        error_msg = f"PDF content from {pdf_path} - Text extraction failed. This PDF may require OCR processing or the content may be in image format."
        print(f"❌ {error_msg}")
        return error_msg
    
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
        """Extract basic information from resume text using regex."""
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
    
    def _parse_with_llm(self, resume_text: str, llm) -> Dict[str, Any]:
        """Use LLM to parse resume text into structured data."""
        
        print(f"🤖 Sending {len(resume_text)} characters to LLM for parsing")
        print(f"📄 First 500 characters: {resume_text[:500]}...")
        
        # Create a comprehensive prompt for LLM parsing
        prompt = f"""
You are an expert resume parser. Extract structured information from the following resume text and return it as a JSON object.

RESUME TEXT:
{resume_text[:8000]}  # Limit text length to avoid token limits

IMPORTANT INSTRUCTIONS:
1. This resume may contain LaTeX formatting commands like \\textbf{{}}, \\href{{}}{{}}, \\newcommand{{}}{{}}, etc.
2. Clean up any LaTeX commands and extract the actual content
3. For links in \\href{{url}}{{text}} format, extract the URL from the first braces
4. For \\newcommand{{name}}{{value}} commands, extract the value
5. Look for patterns like "\\textbf{{Technical Skills}}" and extract the skills listed after them
6. Find education entries that may be formatted with \\resumeSubheading commands
7. Find project entries that may be formatted with \\resumeProject commands
8. If this is PDF content, look for page separators (--- Page X ---) and extract content from all pages
9. Handle PDF formatting issues like line breaks, spacing, and layout artifacts
10. Extract information even if the formatting is imperfect or contains OCR artifacts

CRITICAL EMAIL EXTRACTION:
- Look VERY carefully for email addresses in the resume text
- Common email patterns: name@domain.com, name@company.com, etc.
- Check in contact sections, headers, footers, and throughout the document
- If you find any email-like text, extract it as the email field
- If no email is found, leave the email field as empty string but add a warning in parse_warnings

CRITICAL: You MUST return the JSON in EXACTLY this format with these exact field names and structure:

{{
    "candidate_name": "Full name of the candidate",
    "email": "Primary email address (REQUIRED - look carefully for this)",
    "phone": "Primary phone number", 
    "linkedin": "LinkedIn profile URL",
    "github": "GitHub profile URL",
    "portfolio": "Portfolio website URL",
    "education": [
        {{
            "school": "School/University name",
            "degree": "Degree or qualification",
            "start_date": "Start date (YYYY)",
            "end_date": "End date (YYYY) or 'Present'"
        }}
    ],
    "experience": [
        {{
            "company": "Company name",
            "title": "Job title",
            "start_date": "Start date (YYYY-MM)",
            "end_date": "End date (YYYY-MM) or 'Present'",
            "description": "Brief description of role and achievements"
        }}
    ],
    "skills": {{
        "primary": ["skill1", "skill2"],
        "secondary": ["skill3", "skill4"],
        "tools": ["tool1", "tool2"]
    }},
    "projects": [
        {{
            "name": "Project name",
            "description": "Project description",
            "tech_stack": ["tech1", "tech2"],
            "link": "Project link (if available)"
        }}
    ],
    "other_links": ["url1", "url2"],
    "parse_warnings": ["Any warnings or issues during parsing"]
}}

SPECIFIC GUIDELINES:
- EMAIL IS CRITICAL: Search thoroughly for email addresses in all formats
- If a field is not found, use empty string for strings, empty list for arrays
- Extract all links you can find (GitHub, LinkedIn, portfolio, project links, etc.)
- Categorize skills appropriately (programming languages as primary, frameworks as secondary, tools as tools)
- Be thorough but accurate - don't make up information
- Clean up LaTeX formatting before extracting content
- Handle PDF formatting issues gracefully
- Look for information across all pages if it's a multi-page PDF
- Return ONLY the JSON object, no additional text
- Use EXACT field names as shown above - do not change or add any field names

JSON OUTPUT:
"""
        
        try:
            print("🤖 Calling LLM...")
            # Create a message for the LLM
            from portia.model import Message
            message = Message(role="user", content=prompt)
            
            # Call the LLM using the correct method
            response = llm.get_response([message])
            
            # Parse the JSON response
            response_text = response.content
            print(f"🤖 LLM response length: {len(response_text)} characters")
            print(f"🤖 LLM response preview: {response_text[:200]}...")
            
            # Save LLM response preview to output file
            self._save_llm_response_preview(response_text, resume_text[:100])
            
            # Find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                print(f"🤖 Found JSON: {len(json_str)} characters")
                parsed_data = json.loads(json_str)
                print(f"✅ Successfully parsed JSON with keys: {list(parsed_data.keys())}")
            else:
                raise ValueError("No valid JSON found in LLM response")
                
        except Exception as e:
            print(f"❌ LLM parsing failed: {str(e)}")
            # Fallback to basic parsing if LLM fails
            parsed_data = self._fallback_parsing(resume_text)
            parsed_data["parse_warnings"] = [f"LLM parsing failed: {str(e)}. Using fallback parsing."]
        
        return parsed_data
    
    def _save_llm_response_preview(self, llm_response: str, resume_preview: str) -> None:
        """Save LLM response preview to output/{file_name}.json file."""
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename based on resume preview content
            content_hash = hashlib.md5(resume_preview.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            filename = f"llm_response_{timestamp}_{content_hash}.json"
            
            # Extract clean JSON from LLM response
            clean_json = self._extract_clean_json(llm_response)
            
            # Save the clean JSON directly
            output_path = output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(clean_json, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Clean LLM response JSON saved to: {output_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to save LLM response preview: {str(e)}")
    
    def _extract_clean_json(self, llm_response: str) -> Dict[str, Any]:
        """Extract clean JSON from LLM response, removing markdown formatting."""
        # Remove markdown code blocks
        response_clean = llm_response.strip()
        
        # Remove ```json and ``` markers
        if response_clean.startswith('```json'):
            response_clean = response_clean[7:]  # Remove ```json
        elif response_clean.startswith('```'):
            response_clean = response_clean[3:]  # Remove ```
        
        if response_clean.endswith('```'):
            response_clean = response_clean[:-3]  # Remove trailing ```
        
        # Find JSON content between braces
        start_idx = response_clean.find('{')
        end_idx = response_clean.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_clean[start_idx:end_idx]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse extracted JSON: {e}")
                # Return the raw response as fallback
                return {"raw_response": llm_response, "parse_error": str(e)}
        else:
            print("⚠️ No JSON found in LLM response")
            return {"raw_response": llm_response, "parse_error": "No JSON found"}
    
    def _fallback_parsing(self, resume_text: str) -> Dict[str, Any]:
        """Fallback parsing method if LLM fails."""
        # Basic regex-based parsing as fallback
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        phone_match = re.search(r'\b\d{10}\b', resume_text)
        
        # Extract links
        github_links = re.findall(r'https?://github\.com/[^\s\)]+', resume_text)
        linkedin_links = re.findall(r'https?://linkedin\.com/[^\s\)]+', resume_text)
        
        return {
            "candidate_name": "Extracted from resume",
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "linkedin": linkedin_links[0] if linkedin_links else "",
            "github": github_links[0] if github_links else "",
            "portfolio": "",
            "education": [],
            "experience": [],
            "skills": {"primary": [], "secondary": [], "tools": []},
            "projects": [],
            "other_links": [],
            "parse_warnings": ["Used fallback parsing due to LLM failure"]
        }

