"""Job matching tool for analyzing candidate-job compatibility."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List, Dict, TYPE_CHECKING

from pydantic import BaseModel

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input

from utils.schemas import JobDescription, RepositoryAnalysis, CandidateFacts

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from agents.github_agent import GitHubProfileData


class JobMatchResult(BaseModel):
    """Result of job-candidate matching analysis."""
    
    candidate_info: dict[str, Any]
    job_description: JobDescription
    github_analysis: Optional[Any] = None  # GitHubProfileData to avoid circular import
    relevant_repositories: List[RepositoryAnalysis] = []
    code_analysis: Dict[str, Any] = {}
    skill_matches: List[Dict[str, Any]] = []
    overall_assessment: str = ""
    recommendations: List[str] = []
    match_score: float = 0.0
    score_breakdown: Optional[Dict[str, Any]] = None


class JobMatcher:
    """Tool for intelligent job-candidate matching and assessment."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
    
    def parse_job_description(self, job_description_path: str) -> JobDescription:
        """Parse job description using LLM analysis."""
        
        job_path = Path(job_description_path)
        if not job_path.exists():
            raise FileNotFoundError(f"Job description file not found: {job_description_path}")
        
        with open(job_path, 'r', encoding='utf-8') as f:
            job_text = f.read()
        
        # create plan for job description parsing
        plan = self._create_job_parsing_plan()
        result = self.portia.run_plan(plan, plan_run_inputs={"job_description": job_text})
        
        # get the final output which should contain the consolidated data
        if result.outputs.final_output:
            parsed_data = result.outputs.final_output.get_value()
        else:
            # fallback: get the last step output
            step_outputs = list(result.outputs.step_outputs.values())
            parsed_data = step_outputs[-1].get_value() if step_outputs else {}
        
        return self._convert_to_job_description(parsed_data, job_text)
    
    def _create_job_parsing_plan(self) -> PlanBuilderV2:
        """Create a plan for parsing job descriptions."""
        
        plan = PlanBuilderV2(label="Parse job description")
        
        # define input
        plan.input(name="job_description", description="The job description text to parse")
        
        # extract job basics
        plan.llm_step(
            task="Extract job title, company, location, role type, and seniority level from the job description",
            inputs=[Input("job_description")]
        )
        
        # identify required skills
        plan.llm_step(
            task="Identify all required technical skills and technologies from the job description",
            inputs=[Input("job_description")]
        )
        
        # identify preferred skills
        plan.llm_step(
            task="Identify preferred or nice-to-have skills and technologies from the job description",
            inputs=[Input("job_description")]
        )
        
        # identify frameworks and tools
        plan.llm_step(
            task="Identify specific frameworks, libraries, and tools mentioned in the job description",
            inputs=[Input("job_description")]
        )
        
        # consolidate results
        plan.llm_step(
            task="Consolidate all parsed job information into a structured format with job_basics, required_skills, preferred_skills, and frameworks_tools",
            inputs=[Input("job_description")]
        )
        
        return plan.build()
    
    def _convert_to_job_description(self, parsed_data: Dict[str, Any], original_text: str) -> JobDescription:
        """Convert parsed data to JobDescription object."""
        
        # since we're getting raw LLM output, we need to handle it more flexibly
        if isinstance(parsed_data, str):
            # if it's a string, try to extract information from it
            return self._extract_job_info_from_text(parsed_data, original_text)
        
        job_basics = parsed_data.get("job_basics", {})
        required_skills = parsed_data.get("required_skills", [])
        preferred_skills = parsed_data.get("preferred_skills", [])
        frameworks_tools = parsed_data.get("frameworks_tools", [])
        
        return JobDescription(
            title=job_basics.get("title", "Unknown Position"),
            company=job_basics.get("company"),
            location=job_basics.get("location"),
            description=original_text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            technologies=required_skills + preferred_skills,
            frameworks=frameworks_tools,
            role_type=job_basics.get("role_type", ""),
            seniority_level=job_basics.get("seniority_level", "")
        )
    
    def _extract_job_info_from_text(self, text: str, original_text: str) -> JobDescription:
        """Extract job information from LLM output text."""
        
        # simple extraction based on common patterns
        title = "Unknown Position"
        company = None
        location = None
        required_skills = []
        preferred_skills = []
        frameworks = []
        
        # extract title
        if "frontend" in text.lower():
            title = "Frontend Engineer"
        elif "backend" in text.lower():
            title = "Backend Engineer"
        elif "full stack" in text.lower():
            title = "Full Stack Engineer"
        
        # extract skills
        skill_keywords = ["javascript", "python", "react", "node.js", "html", "css", "java", "sql"]
        for skill in skill_keywords:
            if skill in text.lower():
                required_skills.append(skill.title())
        
        return JobDescription(
            title=title,
            company=company,
            location=location,
            description=original_text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            technologies=required_skills + preferred_skills,
            frameworks=frameworks,
            role_type="",
            seniority_level=""
        )
    
    def convert_candidate_facts_to_dict(self, candidate_facts: CandidateFacts) -> dict:
        """Convert CandidateFacts to dictionary format."""
        
        return {
            "candidate_name": candidate_facts.candidate.full_name or "Unknown",
            "email": candidate_facts.candidate.emails[0] if candidate_facts.candidate.emails else "",
            "phone": candidate_facts.candidate.phones[0] if candidate_facts.candidate.phones else "",
            "linkedin": candidate_facts.candidate.linkedin or "",
            "github": candidate_facts.candidate.github[0] if candidate_facts.candidate.github else "",
            "portfolio": candidate_facts.candidate.portfolio[0] if candidate_facts.candidate.portfolio else "",
            "education": [
                {
                    "school": edu.school,
                    "degree": edu.degree,
                    "start_date": edu.start,
                    "end_date": edu.end
                }
                for edu in candidate_facts.education
            ],
            "experience": [
                {
                    "company": exp.company,
                    "title": exp.role,
                    "start_date": exp.start,
                    "end_date": exp.end,
                    "description": " ".join(exp.bullets)
                }
                for exp in candidate_facts.experience
            ],
            "skills": {
                "primary": candidate_facts.skills.primary,
                "secondary": candidate_facts.skills.secondary,
                "tools": candidate_facts.skills.tools
            },
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description or "",
                    "tech_stack": proj.tech,
                    "link": proj.link or ""
                }
                for proj in candidate_facts.projects
            ]
        }
    
    def save_analysis_results(self, result: JobMatchResult) -> None:
        """Save analysis results to file."""
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # handle different possible candidate name fields
        candidate_name = "Unknown"
        if result.candidate_info.get('candidate_name'):
            candidate_name = result.candidate_info['candidate_name']
        elif result.candidate_info.get('name'):
            candidate_name = result.candidate_info['name']
        
        filename = f"enhanced_analysis_{candidate_name.replace(' ', '_')}_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, indent=2, ensure_ascii=False)
        
        print(f"💾 Enhanced analysis results saved to: {filepath}")
