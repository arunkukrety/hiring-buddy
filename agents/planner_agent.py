"""Planner Agent for orchestrating the complete analysis workflow."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput

from .github_agent import GitHubAgent
from .resume_agent import ResumeAgent
from tools.job_matcher import JobMatcher, JobMatchResult
from tools.skill_matcher import SkillMatcher
from tools.repository_analyzer import RepositoryAnalyzer
from tools.assessment_generator import AssessmentGenerator
from tools.code_analyzer import CodeAnalyzer
from utils.schemas import CandidateFacts, JobDescription, RepositoryAnalysis
from .github_agent import GitHubProfileData


class ResumeAnalysisResult(BaseModel):
    """Result of resume analysis."""
    
    candidate_info: Dict[str, Any]
    candidate_facts: CandidateFacts
    github_analysis: Optional[GitHubProfileData] = None
    job_match_result: Optional[JobMatchResult] = None


class PlannerAgent:
    """Planner agent that orchestrates the complete analysis workflow using tools."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
        self.resume_agent = ResumeAgent(portia)
        self.github_agent = GitHubAgent(portia)
    
        # initialize tools
        self.job_matcher = JobMatcher(portia)
        self.skill_matcher = SkillMatcher()
        self.repository_analyzer = RepositoryAnalyzer()
        self.assessment_generator = AssessmentGenerator(portia)
        self.code_analyzer = CodeAnalyzer()
    
    def analyze_resume(self, resume_path: str, job_description_path: str = None) -> ResumeAnalysisResult:
        """Complete workflow: resume → github → job matching → code analysis → assessment."""
        
        print("🤖 Planner Agent: Starting complete analysis workflow")
        
        try:
            # step 1: parse resume
            print("📄 Step 1: Parsing resume...")
            candidate_facts = self.resume_agent.parse_resume(resume_path)
            candidate_info = self.job_matcher.convert_candidate_facts_to_dict(candidate_facts)
            
            # validate email extraction
            if not candidate_info.get('email') or candidate_info['email'].strip() == "":
                print("⚠️ No email found in resume. Attempting to extract from GitHub profile...")
                
                # try to get email from GitHub profile if available
                if candidate_facts.candidate.github:
                    github_url = candidate_facts.candidate.github[0]
                    print(f"🔍 Checking GitHub profile for email: {github_url}")
                    
                    # get GitHub profile data
                    github_analysis = self.github_agent.get_comprehensive_profile(github_url)
                    if github_analysis and hasattr(github_analysis, 'email') and github_analysis.email:
                        candidate_info['email'] = github_analysis.email
                        print(f"✅ Found email in GitHub profile: {github_analysis.email}")
                    else:
                        print("⚠️ No email found in GitHub profile either")
                        candidate_info['email'] = ""  # ensure it's empty string
                else:
                    print("⚠️ No GitHub profile available to check for email")
                    candidate_info['email'] = ""
            
            # final email validation
            if not candidate_info.get('email') or candidate_info['email'].strip() == "":
                print("❌ CRITICAL: No email address found for candidate!")
                print("📧 Please ensure the resume contains a valid email address")
                print("📧 The system requires an email to send interview invitations")
                print("📧 You can manually add the email to the resume or provide it separately")
                
                # ask user for email input
                manual_email = input("\n📧 Please enter the candidate's email address (or press Enter to continue without email): ").strip()
                if manual_email:
                    candidate_info['email'] = manual_email
                    print(f"✅ Using manually provided email: {manual_email}")
                else:
                    print("⚠️ Continuing without email address - interview scheduling may fail")
            
            # step 2: analyze github profile
            print("🐙 Step 2: Analyzing GitHub profile...")
            github_analysis = None
            if candidate_facts.candidate.github:
                github_url = candidate_facts.candidate.github[0]
                github_analysis = self.github_agent.get_comprehensive_profile(github_url)
            
            # step 3: job matching (if job description provided)
            job_match_result = None
            if job_description_path:
                print("🎯 Step 3: Performing job-candidate matching...")
                job_match_result = self._perform_job_matching(
                    candidate_info, candidate_facts, github_analysis, job_description_path
                )
            
            # create result
            result = ResumeAnalysisResult(
                candidate_info=candidate_info,
                candidate_facts=candidate_facts,
                github_analysis=github_analysis,
                job_match_result=job_match_result
            )
            
            print("✅ Planner Agent: Workflow completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Planner Agent: Workflow failed: {str(e)}")
            raise
    
    def _perform_job_matching(
        self, 
        candidate_info: dict, 
        candidate_facts: CandidateFacts,
        github_analysis: Optional[GitHubProfileData], 
        job_description_path: str
    ) -> JobMatchResult:
        """Perform complete job matching workflow using tools."""
        
        # step 1: parse job description
        print("📋 Step 3.1: Parsing job description...")
        job_description = self.job_matcher.parse_job_description(job_description_path)
        
        # step 2: intelligent skill matching
        print("🎯 Step 3.2: Performing intelligent skill matching...")
        skill_matches = self.skill_matcher.intelligent_skill_matching_with_info(
            candidate_info, job_description, github_analysis
        )
        
        # step 3: identify relevant repositories
        print("🔍 Step 3.3: Identifying job-relevant repositories...")
        relevant_repos = self.repository_analyzer.identify_relevant_repositories(
            github_analysis, job_description
        )
        
        # step 4: perform deep code analysis
        print("💻 Step 3.4: Performing deep code analysis...")
        code_analysis = {}
        if candidate_facts.candidate.github:
            github_url = candidate_facts.candidate.github[0]
            code_analysis = self.code_analyzer.analyze_repository_code_deep(
                relevant_repos, job_description, github_url, self.github_agent
            )
        
        # step 5: generate comprehensive assessment
        print("📊 Step 3.5: Generating comprehensive assessment...")
        
        # add resume text to candidate info for skills extraction
        candidate_info_with_resume = candidate_info.copy()
        candidate_info_with_resume['resume_text'] = candidate_facts.resume_text or ''
        
        assessment = self.assessment_generator.generate_comprehensive_assessment_with_info(
            candidate_info_with_resume, job_description, github_analysis, 
            relevant_repos, code_analysis, skill_matches
        )
        
        # create final result
        result = JobMatchResult(
            candidate_info=candidate_info,
            job_description=job_description,
            github_analysis=github_analysis,
            relevant_repositories=relevant_repos,
            code_analysis=code_analysis,
            skill_matches=skill_matches,
            overall_assessment=assessment["overall_assessment"],
            recommendations=assessment["recommendations"],
            match_score=assessment["match_score"],
            score_breakdown=assessment.get("score_breakdown")
        )
        
        # save results
        self.job_matcher.save_analysis_results(result)
        
        return result
    
    def create_analysis_plan(self, resume_path: str) -> PlanBuilderV2:
        """Create a plan for resume analysis."""
        
        plan = PlanBuilderV2(label="Resume Analysis")
        
        # define input
        plan.input(name="resume_path", description="Path to the resume file")
        
        # parse resume
        plan.llm_step(
            task="Parse the resume and extract candidate information including skills, experience, education, and contact details",
            inputs=[Input("resume_path")]
        )
        
        # analyze github profile
        plan.llm_step(
            task="Extract GitHub URL from resume and analyze the candidate's GitHub profile for activity, repositories, and contributions",
            inputs=[Input("resume_path")]
        )
        
        # consolidate results
        plan.llm_step(
            task="Consolidate all analysis results into a comprehensive candidate profile with skills, experience, and GitHub activity",
            inputs=[Input("resume_path")]
        )
        
        return plan.build()
