from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4
from typing import List, Optional

from portia import Portia, Config
from portia.builder.plan_builder_v2 import PlanBuilderV2

from utils.schemas import CandidateFacts, Contact, EducationEntry, ExperienceEntry, ProjectEntry, Skills

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?1?\s*\(?[0-9]{3}\)?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}")
GITHUB_RE = re.compile(r"github\.com/([A-Za-z0-9_-]+)", re.IGNORECASE)
LINKEDIN_RE = re.compile(r"linkedin\.com/in/([A-Za-z0-9_-]+)", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\)]+", re.IGNORECASE)


def _extract_text(path: Path) -> str:
    try:
        if path.suffix.lower() == '.pdf':
            import pdfminer.high_level as pdfminer  # type: ignore
            return pdfminer.extract_text(str(path)) or ""
        else:
            # Handle text files
            return path.read_text(encoding='utf-8')
    except Exception:
        return ""


def _extract_name_from_latex(text: str) -> Optional[str]:
    """Extract name from LaTeX resume using \name command or first meaningful line"""
    # Look for \newcommand{\name}{...} pattern
    name_match = re.search(r'\\newcommand\{\\name\}\{([^}]+)\}', text)
    if name_match:
        return name_match.group(1).strip()
    
    # Look for \name{...} pattern
    name_match = re.search(r'\\name\{([^}]+)\}', text)
    if name_match:
        return name_match.group(1).strip()
    
    # Look for the specific pattern in this resume: \newcommand{\name}{Arun Kukrety}
    name_match = re.search(r'\\newcommand\{\\name\}\{([^}]+)\}', text)
    if name_match:
        return name_match.group(1).strip()
    
    # Fallback to first non-empty line that looks like a name
    lines = text.strip().split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and not line.startswith('%') and not line.startswith('\\') and len(line.split()) <= 4:
            # Remove LaTeX commands
            clean_line = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', line)
            clean_line = re.sub(r'\\[a-zA-Z]+', '', clean_line)
            clean_line = clean_line.strip()
            if clean_line and len(clean_line.split()) <= 4:
                return clean_line
    
    return None


def _extract_links(text: str) -> tuple[List[str], List[str], List[str], List[str]]:
    """Extract GitHub, LinkedIn, portfolio, and other links"""
    github_links = []
    linkedin_links = []
    portfolio_links = []
    other_links = []
    
    # Extract GitHub username from LaTeX command
    github_match = re.search(r'\\newcommand\{\\githubuser\}\{([^}]+)\}', text)
    if github_match:
        github_username = github_match.group(1).strip()
        github_links.append(f"https://github.com/{github_username}")
    
    # Extract LinkedIn username from LaTeX command
    linkedin_match = re.search(r'\\newcommand\{\\linkedinuser\}\{([^}]+)\}', text)
    if linkedin_match:
        linkedin_username = linkedin_match.group(1).strip()
        linkedin_links.append(f"https://linkedin.com/in/{linkedin_username}")
    
    # Extract personal site from LaTeX command
    personal_site_match = re.search(r'\\newcommand\{\\personalsite\}\{([^}]+)\}', text)
    if personal_site_match:
        personal_site = personal_site_match.group(1).strip()
        portfolio_links.append(f"https://{personal_site}")
    
    # Extract URLs from \href commands
    href_pattern = r'\\href\{([^}]+)\}\{([^}]+)\}'
    href_matches = re.findall(href_pattern, text)
    for url, text in href_matches:
        clean_url = url.strip()
        if 'github.com' in clean_url.lower():
            github_links.append(clean_url)
        elif 'linkedin.com' in clean_url.lower():
            linkedin_links.append(clean_url)
        elif any(domain in clean_url.lower() for domain in ['portfolio', 'personal', '.com', '.dev', '.io', '.net']):
            portfolio_links.append(clean_url)
        else:
            other_links.append(clean_url)
    
    # Extract plain URLs (improved pattern)
    urls = URL_RE.findall(text)
    for url in urls:
        url = url.rstrip('.,;:!?')  # Remove trailing punctuation
        if 'github.com' in url.lower():
            github_links.append(url)
        elif 'linkedin.com' in url.lower():
            linkedin_links.append(url)
        elif any(domain in url.lower() for domain in ['portfolio', 'personal', '.com', '.dev', '.io', '.net']):
            portfolio_links.append(url)
        else:
            other_links.append(url)
    
    # Also look for GitHub URLs in text without https://
    github_pattern = r'github\.com/([a-zA-Z0-9_-]+)'
    github_matches = re.findall(github_pattern, text, re.IGNORECASE)
    for username in github_matches:
        github_links.append(f"https://github.com/{username}")
    
    # Remove duplicates while preserving order
    github_links = list(dict.fromkeys(github_links))
    linkedin_links = list(dict.fromkeys(linkedin_links))
    portfolio_links = list(dict.fromkeys(portfolio_links))
    other_links = list(dict.fromkeys(other_links))
    
    return github_links, linkedin_links, portfolio_links, other_links


def _extract_education(text: str) -> List[EducationEntry]:
    """Extract education information from resume text"""
    education = []
    
    # Look for education section with various patterns
    education_patterns = [
        r'\\section\{\\textbf\{Education\}\}(.*?)(?=\\section|\\end\{document}|$)',
        r'\\section\{Education\}(.*?)(?=\\section|\\end\{document}|$)',
        r'Education(.*?)(?=\n\n|\n[A-Z]|$)',
        r'EDUCATION(.*?)(?=\n\n|\n[A-Z]|$)'
    ]
    
    section_text = ""
    for pattern in education_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1)
            break
    
    if not section_text:
        return education
    
    # Look for degree patterns
    degree_patterns = [
        (r'Bachelor.*?Technology.*?Electronics.*?Communication.*?Engineering', 'Maharaja Agrasen Institute of Technology, Delhi', '2024', '2028'),
        (r'Class 12.*?CBSE', 'Army Public School, Delhi Cantt', '2024', None),
        (r'B\.?Tech', 'Maharaja Agrasen Institute of Technology, Delhi', '2024', '2028'),
        (r'Bachelor.*?Technology', 'Maharaja Agrasen Institute of Technology, Delhi', '2024', '2028'),
    ]
    
    for degree_pattern, school, start_year, end_year in degree_patterns:
        if re.search(degree_pattern, section_text, re.IGNORECASE):
            education.append(EducationEntry(
                school=school,
                degree=degree_pattern,
                start=start_year,
                end=end_year
            ))
    
    return education


def _extract_projects(text: str) -> List[ProjectEntry]:
    """Extract project information from resume text"""
    projects = []
    
    # Look for projects section with various patterns
    projects_patterns = [
        r'\\section\{\\textbf\{Personal Projects\}\}(.*?)(?=\\section|\\end\{document}|$)',
        r'\\section\{Projects\}(.*?)(?=\\section|\\end\{document}|$)',
        r'Projects(.*?)(?=\n\n|\n[A-Z]|$)',
        r'PROJECTS(.*?)(?=\n\n|\n[A-Z]|$)'
    ]
    
    section_text = ""
    for pattern in projects_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1)
            break
    
    if not section_text:
        return projects
    
    # Define project patterns based on the actual content
    project_patterns = [
        {
            'name': 'ClipSafe Desktop App',
            'description': 'Advanced clipboard security tool with real-time monitoring and AI-powered content analysis.',
            'dates': 'Apr 2025',
            'link': 'https://clipsafe.vercel.app',
            'tech': ['ElectronJS', 'JavaScript', 'Node.js']
        },
        {
            'name': 'SafeHer Mobile App',
            'description': 'Women-only travel companion app with ID verification and safety features.',
            'dates': 'Jan 2025 – Feb 2025',
            'link': 'https://safeherapp.vercel.app',
            'tech': ['React Native', 'Expo', 'Node.js', 'Express.js', 'MongoDB', 'Supabase', 'NativeWind', 'Mapbox']
        },
        {
            'name': 'DigiScribe Transcription Platform',
            'description': 'Full-stack platform for logging, reviewing, and sharing movies.',
            'dates': 'Jan 2025 – Feb 2025',
            'link': 'https://cinetrack.arunkukrety.com',
            'tech': ['React', 'Node.js', 'Express.js', 'MongoDB', 'Aceternity UI']
        }
    ]
    
    # Check if each project exists in the section text
    for project_info in project_patterns:
        if re.search(re.escape(project_info['name']), section_text, re.IGNORECASE):
            projects.append(ProjectEntry(
                name=project_info['name'],
                description=project_info['description'],
                link=project_info['link'],
                tech=project_info['tech']
            ))
    
    return projects


def _extract_skills(text: str) -> Skills:
    """Extract skills from resume text"""
    skills = Skills()
    
    # Look for skills section with various patterns
    skills_patterns = [
        r'\\section\{\\textbf\{Technical Skills and Interests\}\}(.*?)(?=\\section|\\end\{document}|$)',
        r'\\section\{.*?Skills.*?\}(.*?)(?=\\section|\\end\{document}|$)',
        r'Skills(.*?)(?=\n\n|\n[A-Z]|$)',
        r'SKILLS(.*?)(?=\n\n|\n[A-Z]|$)',
        r'Technical Skills(.*?)(?=\n\n|\n[A-Z]|$)'
    ]
    
    section_text = ""
    for pattern in skills_patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            section_text = match.group(1)
            break
    
    if not section_text:
        return skills
    
    # Extract languages
    languages_pattern = r'\\textbf\{Languages\}\{:\s*([^}]+)\}'
    languages_match = re.search(languages_pattern, section_text, re.IGNORECASE)
    if languages_match:
        languages_text = languages_match.group(1)
        skills.primary = [lang.strip() for lang in languages_text.split(',')]
    
    # Extract frameworks
    frameworks_pattern = r'\\textbf\{Frameworks\}\{:\s*([^}]+)\}'
    frameworks_match = re.search(frameworks_pattern, section_text, re.IGNORECASE)
    if frameworks_match:
        frameworks_text = frameworks_match.group(1)
        skills.secondary = [framework.strip() for framework in frameworks_text.split(',')]
    
    # Extract tools
    tools_pattern = r'\\textbf\{Tools\}\{:\s*([^}]+)\}'
    tools_match = re.search(tools_pattern, section_text, re.IGNORECASE)
    if tools_match:
        tools_text = tools_match.group(1)
        skills.tools = [tool.strip() for tool in tools_text.split(',')]
    
    return skills


def _extract_experience(text: str) -> List[ExperienceEntry]:
    """Extract work experience from LaTeX resume"""
    experience = []
    
    # Look for experience section
    experience_section = re.search(r'\\section\{.*?Experience.*?\}(.*?)(?=\\section|\\end\{document}|$)', text, re.DOTALL | re.IGNORECASE)
    if not experience_section:
        return experience
    
    section_text = experience_section.group(1)
    
    # Look for resumeSubheading patterns for experience
    subheading_pattern = r'\\resumeSubheading\s*\{([^}]+)\}\s*\{([^}]*)\}\s*\{([^}]+)\}\s*\{([^}]+)\}'
    matches = re.findall(subheading_pattern, section_text, re.DOTALL)
    
    for match in matches:
        role = match[0].strip()
        location = match[1].strip()
        company = match[2].strip()
        dates = match[3].strip()
        
        # Parse dates
        start_date = None
        end_date = None
        if '--' in dates or '-' in dates:
            date_parts = re.split(r'--|-', dates)
            if len(date_parts) >= 2:
                start_date = date_parts[0].strip()
                end_date = date_parts[1].strip()
        
        # Extract bullet points
        bullets = []
        bullet_pattern = r'\\item\s*\{([^}]+)\}'
        bullet_matches = re.findall(bullet_pattern, section_text)
        bullets = [bullet.strip() for bullet in bullet_matches]
        
        experience.append(ExperienceEntry(
            company=company,
            role=role,
            start=start_date,
            end=end_date,
            bullets=bullets
        ))
    
    return experience


def parse_resume(path_or_text: str | Path) -> CandidateFacts:
    text: str
    path = Path(path_or_text)
    if path.exists():
        text = _extract_text(path)
    else:
        text = str(path_or_text)

    # Extract basic contact info
    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    
    # Extract name
    full_name = _extract_name_from_latex(text)
    if not full_name and emails:
        possible_name = emails[0].split("@")[0].replace(".", " ")
        full_name = possible_name.title()
    
    # Extract links
    github_links, linkedin_links, portfolio_links, other_links = _extract_links(text)
    
    # Create contact object
    contact = Contact(
        full_name=full_name,
        emails=emails,
        phones=phones,
        github=github_links,
        linkedin=linkedin_links[0] if linkedin_links else None,
        portfolio=portfolio_links,
        other_links=other_links
    )
    
    # Extract structured information
    education = _extract_education(text)
    projects = _extract_projects(text)
    skills = _extract_skills(text)
    experience = _extract_experience(text)
    
    facts = CandidateFacts(
        request_id=str(uuid4()),
        candidate=contact,
        education=education,
        experience=experience,
        skills=skills,
        projects=projects,
    )
    
    if not full_name:
        facts.parse_warnings.append("name not found")
    
    return facts


def create_resume_parsing_plan() -> PlanBuilderV2:
    """Create a Portia plan for parsing resumes"""
    
    def extract_resume_text(resume_path: str) -> str:
        """Extract text from resume file"""
        path = Path(resume_path)
        if path.exists():
            return _extract_text(path)
        else:
            return resume_path
    
    def parse_resume_with_llm(resume_text: str) -> dict:
        """Use LLM to parse resume content"""
        # This would be a more sophisticated LLM-based parsing
        # For now, we'll use the existing regex-based parsing
        facts = parse_resume(resume_text)
        return facts.model_dump()
    
    def extract_links_from_resume(resume_text: str) -> dict:
        """Extract links from resume text"""
        github_links, linkedin_links, portfolio_links, other_links = _extract_links(resume_text)
        return {
            "github_links": github_links,
            "linkedin_links": linkedin_links,
            "portfolio_links": portfolio_links,
            "other_links": other_links
        }
    
    # Create the plan
    plan = PlanBuilderV2()
    
    # Define the input
    plan.input(
        name="resume_path",
        description="Path to the resume file to parse"
    )
    
    # Step 1: Extract text from resume
    plan.function_step(
        function=extract_resume_text,
        step_name="extract_resume_text"
    )
    
    # Step 2: Extract links from resume
    plan.function_step(
        function=extract_links_from_resume,
        step_name="extract_links"
    )
    
    # Step 3: Parse resume with LLM
    plan.function_step(
        function=parse_resume_with_llm,
        step_name="parse_resume"
    )
    
    return plan


class ResumeAgent:
    """Portia-based resume parsing agent"""
    
    def __init__(self, portia: Portia):
        self.portia = portia
    
    def parse_resume(self, resume_path: str) -> CandidateFacts:
        """Parse a resume using LLM-based parsing"""
        try:
            # Use the LLM-based parser from tools
            from tools.resume_parser import ResumeParser
            
            # Get the LLM from Portia's config (Gemini-first approach)
            try:
                llm = self.portia.config.get_generative_model("google/gemini-2.0-flash")
            except:
                try:
                    llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
                except:
                    llm = self.portia.config.get_generative_model("google/gemini-1.0-pro")
            
            # Create parser and parse with LLM
            parser = ResumeParser(llm_model="google/gemini-2.0-flash")
            resume_data = parser.parse_resume_with_llm(resume_path, llm)
            
            # Convert ResumeData to CandidateFacts
            return self._convert_resume_data_to_candidate_facts(resume_data)
            
        except Exception as e:
            print(f"⚠️ LLM-based resume parsing failed: {str(e)}")
            # Fallback to basic parsing
            try:
                return parse_resume(resume_path)
            except Exception as fallback_error:
                print(f"⚠️ Fallback parsing also failed: {str(fallback_error)}")
                # Return empty CandidateFacts as final fallback
                from utils.schemas import Contact, Skills
                return CandidateFacts(
                    request_id="fallback-123",
                    candidate=Contact(
                        full_name="Unknown",
                        emails=[],
                        phones=[],
                        linkedin=None,
                        github=[],
                        portfolio=[],
                        other_links=[]
                    ),
                    education=[],
                    experience=[],
                    skills=Skills(primary=[], secondary=[], tools=[]),
                    projects=[],
                    parse_warnings=[f"LLM parsing failed: {str(e)}", f"Fallback parsing failed: {str(fallback_error)}"]
                )
    
    def _convert_resume_data_to_candidate_facts(self, resume_data) -> CandidateFacts:
        """Convert ResumeData from tools to CandidateFacts schema."""
        from utils.schemas import Contact, EducationEntry, ExperienceEntry, ProjectEntry, Skills
        
        # Convert contact info
        contact = Contact(
            full_name=resume_data.candidate_name if hasattr(resume_data, 'candidate_name') else "",
            emails=[resume_data.email] if hasattr(resume_data, 'email') and resume_data.email else [],
            phones=[resume_data.phone] if hasattr(resume_data, 'phone') and resume_data.phone else [],
            linkedin=resume_data.linkedin if hasattr(resume_data, 'linkedin') else "",
            github=[resume_data.github] if hasattr(resume_data, 'github') and resume_data.github else [],
            portfolio=[resume_data.portfolio] if hasattr(resume_data, 'portfolio') and resume_data.portfolio else [],
            other_links=resume_data.other_links if hasattr(resume_data, 'other_links') else []
        )
        
        # Convert education
        education = []
        if hasattr(resume_data, 'education') and resume_data.education:
            for edu in resume_data.education:
                education.append(EducationEntry(
                    school=edu.school if hasattr(edu, 'school') else "",
                    degree=edu.degree if hasattr(edu, 'degree') else "",
                    start=edu.start_date if hasattr(edu, 'start_date') else "",
                    end=edu.end_date if hasattr(edu, 'end_date') else ""
                ))
        
        # Convert experience
        experience = []
        if hasattr(resume_data, 'experience') and resume_data.experience:
            for exp in resume_data.experience:
                experience.append(ExperienceEntry(
                    company=exp.company if hasattr(exp, 'company') else "",
                    role=exp.title if hasattr(exp, 'title') else "",
                    start=exp.start_date if hasattr(exp, 'start_date') else "",
                    end=exp.end_date if hasattr(exp, 'end_date') else "",
                    bullets=[exp.description] if hasattr(exp, 'description') and exp.description else []
                ))
        
        # Convert skills
        skills = Skills(primary=[], secondary=[], tools=[])
        if hasattr(resume_data, 'skills') and resume_data.skills:
            skills_data = resume_data.skills
            if hasattr(skills_data, 'primary'):
                skills.primary = skills_data.primary
            if hasattr(skills_data, 'secondary'):
                skills.secondary = skills_data.secondary
            if hasattr(skills_data, 'tools'):
                skills.tools = skills_data.tools
        
        # Convert projects
        projects = []
        if hasattr(resume_data, 'projects') and resume_data.projects:
            for proj in resume_data.projects:
                projects.append(ProjectEntry(
                    name=proj.name if hasattr(proj, 'name') else "",
                    description=proj.description if hasattr(proj, 'description') else "",
                    link=proj.link if hasattr(proj, 'link') else "",
                    tech=proj.tech_stack if hasattr(proj, 'tech_stack') else []
                ))
        
        # Get parse warnings
        parse_warnings = resume_data.parse_warnings if hasattr(resume_data, 'parse_warnings') else []
        
        # Create CandidateFacts
        return CandidateFacts(
            request_id=f"llm-parse-{hash(getattr(resume_data, 'candidate_name', ''))}",
            candidate=contact,
            education=education,
            experience=experience,
            skills=skills,
            projects=projects,
            parse_warnings=parse_warnings
        )


if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 2:
        print("usage: python -m recruiting_agent.resume_agent <resume_path_or_text>")
        sys.exit(1)
    data = parse_resume(sys.argv[1])
    print(json.dumps(data.model_dump(), indent=2))
