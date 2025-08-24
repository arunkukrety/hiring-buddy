"""Job Description Parser Agent for analyzing job requirements using Portia's planning system."""

import re
from pathlib import Path
from typing import List, Dict, Any

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput

from utils.schemas import JobDescription, JobRequirement


class JobParserAgent:
    """Job description parser agent using Portia's planning system."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
    
    def parse_job_description(self, job_description_path: str) -> JobDescription:
        """Parse a job description file and extract structured requirements."""
        
        job_path = Path(job_description_path)
        if not job_path.exists():
            raise FileNotFoundError(f"Job description file not found: {job_description_path}")
        
        # read the job description
        with open(job_path, 'r', encoding='utf-8') as f:
            job_text = f.read()
        
        if not job_text.strip():
            raise ValueError("Job description file is empty")
        
        try:
            # use portia's planning system to parse the job description
            plan = self._create_job_parsing_plan()
            result = self.portia.run(plan, inputs={"job_description": job_text})
            
            # extract the parsed data
            parsed_data = result.outputs.get("parsed_job_data", {})
            
            # convert to JobDescription object
            job_desc = self._convert_to_job_description(parsed_data, job_text)
            
            return job_desc
            
        except Exception as e:
            # return a basic job description with the raw text
            return JobDescription(
                title="Unknown Position",
                description=job_text,
                required_skills=[],
                preferred_skills=[],
                technologies=[],
                frameworks=[]
            )
    
    def _create_job_parsing_plan(self) -> PlanBuilderV2:
        """Create a plan for parsing job descriptions."""
        
        plan = PlanBuilderV2()
        
        # step 1: extract basic job information
        plan.add_step(
            "extract_job_basics",
            "Extract basic job information including title, company, location, and role type",
            inputs=[Input("job_description", "The full job description text")],
            outputs=[StepOutput("job_basics", "Basic job information including title, company, location, role type, seniority level, and industry")]
        )
        
        # step 2: identify required skills and technologies
        plan.add_step(
            "identify_required_skills",
            "Identify all required technical skills, programming languages, and technologies mentioned in the job description",
            inputs=[Input("job_description", "The full job description text")],
            outputs=[StepOutput("required_skills", "List of required technical skills and technologies")]
        )
        
        # step 3: identify preferred skills
        plan.add_step(
            "identify_preferred_skills",
            "Identify preferred or nice-to-have skills and technologies mentioned in the job description",
            inputs=[Input("job_description", "The full job description text")],
            outputs=[StepOutput("preferred_skills", "List of preferred skills and technologies")]
        )
        
        # step 4: identify experience requirements
        plan.add_step(
            "identify_experience_requirements",
            "Identify required and preferred experience areas, years of experience, and domain expertise",
            inputs=[Input("job_description", "The full job description text")],
            outputs=[StepOutput("experience_requirements", "Required and preferred experience areas")]
        )
        
        # step 5: identify frameworks and tools
        plan.add_step(
            "identify_frameworks_tools",
            "Identify specific frameworks, libraries, tools, and technologies mentioned in the job description",
            inputs=[Input("job_description", "The full job description text")],
            outputs=[StepOutput("frameworks_tools", "List of frameworks, libraries, and tools mentioned")]
        )
        
        # step 6: consolidate all parsed data
        plan.add_step(
            "consolidate_job_data",
            "Consolidate all parsed job information into a structured format",
            inputs=[
                Input("job_basics", "Basic job information"),
                Input("required_skills", "Required skills and technologies"),
                Input("preferred_skills", "Preferred skills and technologies"),
                Input("experience_requirements", "Experience requirements"),
                Input("frameworks_tools", "Frameworks and tools")
            ],
            outputs=[StepOutput("parsed_job_data", "Complete structured job description data")]
        )
        
        return plan
    
    def _convert_to_job_description(self, parsed_data: Dict[str, Any], original_text: str) -> JobDescription:
        """Convert parsed data to JobDescription object."""
        
        # extract basic information
        job_basics = parsed_data.get("job_basics", {})
        required_skills = parsed_data.get("required_skills", [])
        preferred_skills = parsed_data.get("preferred_skills", [])
        experience_reqs = parsed_data.get("experience_requirements", {})
        frameworks_tools = parsed_data.get("frameworks_tools", [])
        
        # create requirements list with weights
        requirements = []
        
        # add required skills with high weight
        for skill in required_skills:
            requirements.append(JobRequirement(
                requirement=skill,
                category="skills",
                importance="required",
                weight=1.0
            ))
        
        # add preferred skills with medium weight
        for skill in preferred_skills:
            requirements.append(JobRequirement(
                requirement=skill,
                category="skills",
                importance="preferred",
                weight=0.7
            ))
        
        # add experience requirements
        required_exp = experience_reqs.get("required", [])
        for exp in required_exp:
            requirements.append(JobRequirement(
                requirement=exp,
                category="experience",
                importance="required",
                weight=0.9
            ))
        
        preferred_exp = experience_reqs.get("preferred", [])
        for exp in preferred_exp:
            requirements.append(JobRequirement(
                requirement=exp,
                category="experience",
                importance="preferred",
                weight=0.6
            ))
        
        return JobDescription(
            title=job_basics.get("title", "Unknown Position"),
            company=job_basics.get("company"),
            location=job_basics.get("location"),
            description=original_text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            required_experience=experience_reqs.get("required", []),
            preferred_experience=experience_reqs.get("preferred", []),
            technologies=required_skills + preferred_skills,
            frameworks=frameworks_tools,
            requirements=requirements,
            role_type=job_basics.get("role_type", ""),
            seniority_level=job_basics.get("seniority_level", ""),
            industry=job_basics.get("industry")
        )
