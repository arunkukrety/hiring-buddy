"""Planner Agent for Resume Processing using Portia's planning system."""

from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel

from portia import Portia, Config
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput

from .llm_resume_parser import LLMResumeParser, ResumeData
from .github_agent import GitHubAgent, GitHubProfileData


class ResumeAnalysisResult(BaseModel):
    """Result of resume analysis."""
    
    candidate_info: dict[str, Any]
    education_summary: str
    skills_summary: str
    projects_summary: str
    overall_assessment: str
    recommendations: list[str]
    github_analysis: Optional[GitHubProfileData] = None
    


class PlannerAgent:
    """Planner agent that creates and executes plans for resume processing."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
        self.llm_parser = LLMResumeParser()
        self.github_agent = GitHubAgent(portia)
    
    def create_resume_analysis_plan(self) -> PlanBuilderV2:
        """Create a plan for comprehensive resume analysis."""
        
        def analyze_resume_data(resume_data: ResumeData) -> ResumeAnalysisResult:
            """Analyze the parsed resume data and provide insights."""
            
            # Create candidate info summary
            candidate_info = {
                "name": resume_data.candidate_name,
                "email": resume_data.email,
                "phone": resume_data.phone,
                "linkedin": resume_data.linkedin,
                "github": resume_data.github,
                "portfolio": resume_data.portfolio
            }
            
            # Create education summary
            education_summary = f"Education: {len(resume_data.education)} entries found"
            if resume_data.education:
                latest_edu = resume_data.education[0]
                education_summary += f" - Latest: {latest_edu.get('degree', 'N/A')} at {latest_edu.get('school', 'N/A')}"
            
            # Create skills summary
            total_skills = (
                len(resume_data.skills.get('primary', [])) +
                len(resume_data.skills.get('secondary', [])) +
                len(resume_data.skills.get('tools', []))
            )
            skills_summary = f"Skills: {total_skills} total skills across primary, secondary, and tools categories"
            
            # Create projects summary
            projects_summary = f"Projects: {len(resume_data.projects)} projects found"
            if resume_data.projects:
                projects_summary += f" - Latest: {resume_data.projects[0].get('name', 'N/A')}"
            
            # Create overall assessment
            assessment_points = []
            if resume_data.education:
                assessment_points.append("Has educational background")
            if resume_data.experience:
                assessment_points.append(f"Has {len(resume_data.experience)} work experiences")
            if resume_data.projects:
                assessment_points.append(f"Has {len(resume_data.projects)} projects")
            if resume_data.skills.get('primary'):
                assessment_points.append(f"Has {len(resume_data.skills['primary'])} primary skills")
            
            overall_assessment = "Strong candidate" if len(assessment_points) >= 3 else "Developing candidate"
            overall_assessment += f" - {', '.join(assessment_points)}"
            
            # Create recommendations
            recommendations = []
            if not resume_data.linkedin:
                recommendations.append("Consider adding LinkedIn profile")
            if not resume_data.github:
                recommendations.append("Consider adding GitHub profile for technical roles")
            if len(resume_data.projects) < 2:
                recommendations.append("Consider adding more projects to showcase skills")
            if not resume_data.experience:
                recommendations.append("Consider adding work experience or internships")
            
            # Note: GitHub analysis will be handled separately in the main analyze_resume method
            # This function is used in the planning system where we don't have access to the GitHub agent
            
            return ResumeAnalysisResult(
                candidate_info=candidate_info,
                education_summary=education_summary,
                skills_summary=skills_summary,
                projects_summary=projects_summary,
                overall_assessment=overall_assessment,
                recommendations=recommendations
            )
        
        # Create the plan
        plan = PlanBuilderV2("Analyze resume and provide comprehensive insights")
        
        # Define inputs
        plan.input(
            name="resume_path",
            description="Path to the resume file to analyze"
        )
        
        plan.input(
            name="llm_model",
            description="LLM model to use for parsing",
            default_value="gpt-4o"
        )
        
        # Step 1: Parse resume using LLM
        plan.llm_step(
            task="Parse the resume file and extract structured information including candidate name, email, phone, education, experience, skills, and projects. Return the information in a structured format.",
            inputs=[Input("resume_path")],
            step_name="parse_resume"
        )
        
        # Step 2: Analyze the parsed data
        plan.function_step(
            function=analyze_resume_data,
            step_name="analyze_resume",
            args={
                "resume_data": StepOutput("parse_resume")
            }
        )
        
        # Step 3: Generate insights using LLM
        plan.llm_step(
            task="Based on the resume analysis, provide additional insights and suggestions for improvement",
            inputs=[
                StepOutput("parse_resume"),
                StepOutput("analyze_resume")
            ],
            step_name="generate_insights"
        )
        
        # Set final output
        plan.final_output(
            output_schema=ResumeAnalysisResult,
            summarize=True
        )
        
        return plan
    
    def analyze_resume(self, resume_path: str, llm_model: str = "gpt-4o") -> ResumeAnalysisResult:
        """Analyze a resume using the planning system."""
        
        # Check if resume file exists
        if not Path(resume_path).exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        
        # Get the LLM from Portia's config - use the default model
        try:
            # Try Google model first (since we have Google API key)
            llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
        except:
            try:
                # Fallback to OpenAI
                llm = self.portia.config.get_generative_model("openai/gpt-4o")
            except:
                # Use whatever default model is available
                llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
        
        # Use the LLM parser directly for now (simpler approach)
        try:
            resume_data = self.llm_parser.parse_resume(resume_path, llm)
            
            # Create analysis result
            candidate_info = {
                "name": resume_data.candidate_name,
                "email": resume_data.email,
                "phone": resume_data.phone,
                "linkedin": resume_data.linkedin,
                "github": resume_data.github,
                "portfolio": resume_data.portfolio
            }
            
            # Create summaries
            education_summary = f"Education: {len(resume_data.education)} entries found"
            if resume_data.education:
                latest_edu = resume_data.education[0]
                education_summary += f" - Latest: {latest_edu.get('degree', 'N/A')} at {latest_edu.get('school', 'N/A')}"
            
            total_skills = (
                len(resume_data.skills.get('primary', [])) +
                len(resume_data.skills.get('secondary', [])) +
                len(resume_data.skills.get('tools', []))
            )
            skills_summary = f"Skills: {total_skills} total skills across primary, secondary, and tools categories"
            
            projects_summary = f"Projects: {len(resume_data.projects)} projects found"
            if resume_data.projects:
                projects_summary += f" - Latest: {resume_data.projects[0].get('name', 'N/A')}"
            
            # Create assessment
            assessment_points = []
            if resume_data.education:
                assessment_points.append("Has educational background")
            if resume_data.experience:
                assessment_points.append(f"Has {len(resume_data.experience)} work experiences")
            if resume_data.projects:
                assessment_points.append(f"Has {len(resume_data.projects)} projects")
            if resume_data.skills.get('primary'):
                assessment_points.append(f"Has {len(resume_data.skills['primary'])} primary skills")
            
            overall_assessment = "Strong candidate" if len(assessment_points) >= 3 else "Developing candidate"
            overall_assessment += f" - {', '.join(assessment_points)}"
            
            # Create recommendations
            recommendations = []
            if not resume_data.linkedin:
                recommendations.append("Consider adding LinkedIn profile")
            if not resume_data.github:
                recommendations.append("Consider adding GitHub profile for technical roles")
            if len(resume_data.projects) < 2:
                recommendations.append("Consider adding more projects to showcase skills")
            if not resume_data.experience:
                recommendations.append("Consider adding work experience or internships")
            
            # Analyze GitHub profile if available
            github_analysis = None
            if resume_data.github:
                try:
                    print(f"🔍 Analyzing GitHub profile: {resume_data.github}")
                    github_analysis = self.github_agent.analyze_github_profile(resume_data.github)
                    print(f"✅ GitHub analysis completed for {github_analysis.username}")
                except Exception as e:
                    print(f"⚠️ GitHub analysis failed: {str(e)}")
                    github_analysis = GitHubProfileData(
                        username="",
                        profile_url=resume_data.github,
                        is_valid_url=False,
                        scan_errors=[f"GitHub analysis failed: {str(e)}"]
                    )
            
            return ResumeAnalysisResult(
                candidate_info=candidate_info,
                education_summary=education_summary,
                skills_summary=skills_summary,
                projects_summary=projects_summary,
                overall_assessment=overall_assessment,
                recommendations=recommendations,
                github_analysis=github_analysis
            )
            
        except Exception as e:
            # Fallback analysis if parsing fails
            return ResumeAnalysisResult(
                candidate_info={},
                education_summary="Analysis failed",
                skills_summary="Analysis failed", 
                projects_summary="Analysis failed",
                overall_assessment=f"Error during analysis: {str(e)}",
                recommendations=["Please check the resume file format and try again"],
                github_analysis=None
            )
