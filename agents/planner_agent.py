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
        
        try:
            # step 1: parse resume
            print("<h3><strong>📄 Analyzing resume using resume agent...</strong></h3>")
            candidate_facts = self.resume_agent.parse_resume(resume_path)
            candidate_info = self.job_matcher.convert_candidate_facts_to_dict(candidate_facts)
            
            # validate email extraction
            if not candidate_info.get('email') or candidate_info['email'].strip() == "":
                # try to get email from GitHub profile if available
                if candidate_facts.candidate.github:
                    github_url = candidate_facts.candidate.github[0]
                    
                    # get GitHub profile data
                    print("<h3><strong>🔍 Attempting to retrieve email from GitHub profile...</strong></h3>")
                    github_analysis = self.github_agent.get_comprehensive_profile(github_url)
                    if github_analysis and hasattr(github_analysis, 'email') and github_analysis.email:
                        candidate_info['email'] = github_analysis.email
                    else:
                        candidate_info['email'] = ""  # ensure it's empty string
                else:
                    candidate_info['email'] = ""
            
            # final email validation
            if not candidate_info.get('email') or candidate_info['email'].strip() == "":
                email_warning = []
                email_warning.append("<div style='background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444; margin: 10px 0;'>")
                email_warning.append("<h3><strong>❌ CRITICAL: No email address found for candidate!</strong></h3>")
                email_warning.append("<p>📧 The system requires an email to send interview invitations</p>")
                email_warning.append("</div>")
                print('\n'.join(email_warning))
                
                # ask user for email input
                manual_email = input("\n📧 Please enter the candidate's email address (or press Enter to continue without email): ").strip()
                if manual_email:
                    candidate_info['email'] = manual_email
                    email_success = []
                    email_success.append("<div style='background-color: #f0fdf4; padding: 10px; border-radius: 6px; border-left: 3px solid #22c55e;'>")
                    email_success.append(f"<p><strong>✅ Using manually provided email:</strong> {manual_email}</p>")
                    email_success.append("</div>")
                    print('\n'.join(email_success))
                else:
                    email_warning = []
                    email_warning.append("<div style='background-color: #fffbeb; padding: 10px; border-radius: 6px; border-left: 3px solid #f59e0b;'>")
                    email_warning.append("<p><strong>⚠️ Continuing without email</strong> - interview scheduling may fail</p>")
                    email_warning.append("</div>")
                    print('\n'.join(email_warning))
            
            # step 2: analyze github profile
            print("<h3><strong>🐙 Analyzing GitHub profile using GitHub agent...</strong></h3>")
            github_analysis = None
            if candidate_facts.candidate.github:
                github_url = candidate_facts.candidate.github[0]
                github_analysis = self.github_agent.get_comprehensive_profile(github_url)
                
                # Display GitHub analysis results
                if github_analysis and hasattr(github_analysis, 'username'):
                    github_status = []
                    github_status.append("<div style='background-color: #f0fdf4; padding: 10px; border-radius: 6px; border-left: 3px solid #22c55e;'>")
                    github_status.append(f"<p><strong>✅ GitHub Analysis Complete for:</strong> {github_analysis.username}</p>")
                    
                    if github_analysis.contributions:
                        github_status.append(f"<p><strong>📊 Activity:</strong> {github_analysis.contributions.total_commits} commits, {github_analysis.contributions.total_prs} PRs, {github_analysis.contributions.total_contributions} total contributions</p>")
                    
                    if github_analysis.public_repos:
                        github_status.append(f"<p><strong>📁 Repositories:</strong> {github_analysis.public_repos} public repositories analyzed</p>")
                    
                    # Show top languages from repositories
                    if hasattr(github_analysis, 'repositories') and github_analysis.repositories:
                        all_languages = set()
                        for repo in github_analysis.repositories:
                            if hasattr(repo, 'languages') and repo.languages:
                                # repo.languages is a list, not a dict
                                all_languages.update(repo.languages)
                        
                        if all_languages:
                            # Convert set to list and take first 5
                            lang_names = list(all_languages)[:5]
                            github_status.append(f"<p><strong>💻 Top Languages:</strong> {', '.join(lang_names)}</p>")
                    
                    github_status.append("</div>")
                    print('\n'.join(github_status))
                else:
                    github_error = []
                    github_error.append("<div style='background-color: #fef2f2; padding: 10px; border-radius: 6px; border-left: 3px solid #ef4444;'>")
                    github_error.append("<p><strong>⚠️ GitHub analysis completed with limited data</strong></p>")
                    github_error.append("</div>")
                    print('\n'.join(github_error))
            
            # step 3: job matching (if job description provided)
            job_match_result = None
            if job_description_path:
                print("<h3><strong>🎯 Performing job matching using job matcher...</strong></h3>")
                try:
                    job_match_result = self._perform_job_matching(
                        candidate_info, candidate_facts, github_analysis, job_description_path
                    )
                except Exception as job_match_error:
                    # Handle job matching errors (e.g., API quota exceeded)
                    error_output = []
                    error_output.append("<div style='background-color: #fef2f2; padding: 10px; border-radius: 6px; border-left: 3px solid #ef4444;'>")
                    error_output.append("<p><strong>⚠️ Job matching failed due to API limitations</strong></p>")
                    
                    if "quota" in str(job_match_error).lower() or "429" in str(job_match_error):
                        error_output.append("<p>Google API quota exceeded. GitHub analysis will still be available.</p>")
                    else:
                        error_output.append(f"<p>Error: {str(job_match_error)[:100]}...</p>")
                    
                    error_output.append("</div>")
                    print('\n'.join(error_output))
                    job_match_result = None
            
            # create result
            result = ResumeAnalysisResult(
                candidate_info=candidate_info,
                candidate_facts=candidate_facts,
                github_analysis=github_analysis,
                job_match_result=job_match_result
            )
            
            return result
            
        except Exception as e:
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
        job_description = self.job_matcher.parse_job_description(job_description_path)
        
        # step 2: intelligent skill matching
        skill_matches = self.skill_matcher.intelligent_skill_matching_with_info(
            candidate_info, job_description, github_analysis
        )
        
        # step 3: identify relevant repositories
        relevant_repos = self.repository_analyzer.identify_relevant_repositories(
            github_analysis, job_description
        )
        
        # Display repository analysis results
        if relevant_repos:
            repo_status = []
            repo_status.append("<div style='background-color: #fffbeb; padding: 10px; border-radius: 6px; border-left: 3px solid #f59e0b;'>")
            repo_status.append(f"<p><strong>🔍 Repository Analysis:</strong> Found {len(relevant_repos)} relevant repositories for {job_description.title}</p>")
            
            # Show top 3 most relevant repositories
            top_repos = sorted(relevant_repos, key=lambda r: r.relevance_score, reverse=True)[:3]
            for i, repo in enumerate(top_repos, 1):
                repo_status.append(f"<p><strong>#{i}. {repo.name}</strong> (Relevance: {repo.relevance_score:.1f}) - {', '.join(repo.languages_used[:2]) if repo.languages_used else 'No languages detected'}</p>")
            
            repo_status.append("</div>")
            print('\n'.join(repo_status))
        else:
            repo_warning = []
            repo_warning.append("<div style='background-color: #fef2f2; padding: 10px; border-radius: 6px; border-left: 3px solid #ef4444;'>")
            repo_warning.append("<p><strong>⚠️ No relevant repositories found</strong> for the job requirements</p>")
            repo_warning.append("</div>")
            print('\n'.join(repo_warning))
        
        # step 4: perform deep code analysis
        code_analysis = {}
        if candidate_facts.candidate.github:
            github_url = candidate_facts.candidate.github[0]
            code_analysis = self.code_analyzer.analyze_repository_code_deep(
                relevant_repos, job_description, github_url, self.github_agent
            )
            
            # Display code analysis results
            if code_analysis and 'repositories_analyzed' in code_analysis:
                code_status = []
                code_status.append("<div style='background-color: #f0f9ff; padding: 10px; border-radius: 6px; border-left: 3px solid #3b82f6;'>")
                code_status.append(f"<p><strong>💻 Code Analysis:</strong> Analyzed {code_analysis['repositories_analyzed']} repositories in detail</p>")
                
                if code_analysis.get('languages_found'):
                    code_status.append(f"<p><strong>Languages Found:</strong> {', '.join(code_analysis['languages_found'][:5])}</p>")
                
                if code_analysis.get('frameworks_detected'):
                    code_status.append(f"<p><strong>Frameworks Detected:</strong> {', '.join(code_analysis['frameworks_detected'][:3])}</p>")
                
                code_status.append("</div>")
                print('\n'.join(code_status))
        
        # step 5: generate comprehensive assessment
        
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
