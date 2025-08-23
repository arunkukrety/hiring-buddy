"""Candidate Evaluator Agent for comprehensive job-candidate matching using Portia's planning system."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput

from utils.schemas import (
    CandidateEvaluation, EvaluationCategory, SkillMatch, RepositoryAnalysis,
    JobDescription, CandidateFacts
)
from .job_parser_agent import JobParserAgent
from .resume_agent import ResumeAgent
from .enhanced_github_agent import EnhancedGitHubAgent


class CandidateEvaluatorAgent:
    """Candidate evaluator agent that orchestrates the complete evaluation workflow."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
        self.job_parser = JobParserAgent(portia)
        self.resume_agent = ResumeAgent(portia)
        self.github_agent = EnhancedGitHubAgent(portia)
    
    def evaluate_candidate_for_job(self, resume_path: str, job_description_path: str) -> CandidateEvaluation:
        """Evaluate a candidate for a specific job position."""
        
        print(f"🎯 Candidate Evaluator Agent: Starting evaluation process")
        
        try:
            # step 1: parse job description
            print("📋 Step 1: Parsing job description...")
            job_description = self.job_parser.parse_job_description(job_description_path)
            
            # step 2: parse resume
            print("📄 Step 2: Parsing candidate resume...")
            candidate_facts = self.resume_agent.parse_resume(resume_path)
            
            # step 3: analyze github if available
            print("🐙 Step 3: Analyzing GitHub profile...")
            github_analysis = []
            if candidate_facts.candidate.github:
                github_url = candidate_facts.candidate.github[0]
                github_analysis = self.github_agent.analyze_github_for_job(github_url, job_description)
            
            # step 4: perform comprehensive evaluation
            print("📊 Step 4: Performing comprehensive evaluation...")
            evaluation = self._perform_comprehensive_evaluation(
                candidate_facts, job_description, github_analysis
            )
            
            # step 5: save results
            self._save_evaluation_results(evaluation)
            
            print(f"✅ Candidate Evaluator Agent: Evaluation completed successfully")
            return evaluation
            
        except Exception as e:
            print(f"❌ Candidate Evaluator Agent: Evaluation failed: {str(e)}")
            raise
    
    def _perform_comprehensive_evaluation(
        self, 
        candidate_facts: CandidateFacts, 
        job_description: JobDescription, 
        github_analysis: List[RepositoryAnalysis]
    ) -> CandidateEvaluation:
        """Perform comprehensive candidate evaluation."""
        
        # create evaluation plan
        plan = self._create_evaluation_plan()
        
        # prepare inputs for the plan
        inputs = {
            "candidate_data": self._convert_candidate_to_dict(candidate_facts),
            "job_requirements": self._convert_job_to_dict(job_description),
            "github_analysis": [repo.dict() for repo in github_analysis]
        }
        
        # run the evaluation plan
        result = self.portia.run(plan, inputs=inputs)
        
        # extract evaluation results
        evaluation_data = result.outputs.get("evaluation_results", {})
        
        # convert to CandidateEvaluation object
        evaluation = self._convert_to_evaluation_object(
            evaluation_data, candidate_facts, job_description, github_analysis
        )
        
        return evaluation
    
    def _create_evaluation_plan(self) -> PlanBuilderV2:
        """Create a comprehensive evaluation plan."""
        
        plan = PlanBuilderV2()
        
        # step 1: analyze skill matches
        plan.add_step(
            "analyze_skill_matches",
            "Analyze how well the candidate's skills match the job requirements",
            inputs=[
                Input("candidate_data", "Candidate information from resume"),
                Input("job_requirements", "Job requirements and skills")
            ],
            outputs=[StepOutput("skill_analysis", "Detailed skill matching analysis")]
        )
        
        # step 2: evaluate experience relevance
        plan.add_step(
            "evaluate_experience",
            "Evaluate the relevance of candidate's experience to the job requirements",
            inputs=[
                Input("candidate_data", "Candidate experience information"),
                Input("job_requirements", "Job experience requirements")
            ],
            outputs=[StepOutput("experience_evaluation", "Experience relevance evaluation")]
        )
        
        # step 3: analyze github contributions
        plan.add_step(
            "analyze_github_contributions",
            "Analyze GitHub repositories and contributions for technical skills and project quality",
            inputs=[
                Input("github_analysis", "GitHub repository analysis"),
                Input("job_requirements", "Job technical requirements")
            ],
            outputs=[StepOutput("github_evaluation", "GitHub contribution evaluation")]
        )
        
        # step 4: assess overall fit
        plan.add_step(
            "assess_overall_fit",
            "Assess overall candidate fit for the position based on all factors",
            inputs=[
                Input("skill_analysis", "Skill matching results"),
                Input("experience_evaluation", "Experience evaluation"),
                Input("github_evaluation", "GitHub evaluation"),
                Input("job_requirements", "Job requirements")
            ],
            outputs=[StepOutput("overall_assessment", "Overall candidate assessment")]
        )
        
        # step 5: generate final evaluation
        plan.add_step(
            "generate_evaluation",
            "Generate comprehensive evaluation with scoring and recommendations",
            inputs=[
                Input("skill_analysis", "Skill analysis"),
                Input("experience_evaluation", "Experience evaluation"),
                Input("github_evaluation", "GitHub evaluation"),
                Input("overall_assessment", "Overall assessment")
            ],
            outputs=[StepOutput("evaluation_results", "Complete evaluation results")]
        )
        
        return plan
    
    def _convert_candidate_to_dict(self, candidate_facts: CandidateFacts) -> Dict[str, Any]:
        """Convert candidate facts to dictionary format."""
        
        return {
            "name": candidate_facts.candidate.full_name or "Unknown",
            "email": candidate_facts.candidate.emails[0] if candidate_facts.candidate.emails else "",
            "skills": {
                "primary": candidate_facts.skills.primary,
                "secondary": candidate_facts.skills.secondary,
                "tools": candidate_facts.skills.tools
            },
            "experience": [
                {
                    "company": exp.company,
                    "role": exp.role,
                    "start_date": exp.start,
                    "end_date": exp.end,
                    "description": " ".join(exp.bullets)
                }
                for exp in candidate_facts.experience
            ],
            "education": [
                {
                    "school": edu.school,
                    "degree": edu.degree,
                    "start_date": edu.start,
                    "end_date": edu.end
                }
                for edu in candidate_facts.education
            ],
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description or "",
                    "tech_stack": proj.tech,
                    "link": proj.link or ""
                }
                for proj in candidate_facts.projects
            ],
            "github_urls": candidate_facts.candidate.github
        }
    
    def _convert_job_to_dict(self, job_description: JobDescription) -> Dict[str, Any]:
        """Convert job description to dictionary format."""
        
        return {
            "title": job_description.title,
            "company": job_description.company,
            "required_skills": job_description.required_skills,
            "preferred_skills": job_description.preferred_skills,
            "required_experience": job_description.required_experience,
            "preferred_experience": job_description.preferred_experience,
            "technologies": job_description.technologies,
            "frameworks": job_description.frameworks,
            "role_type": job_description.role_type,
            "seniority_level": job_description.seniority_level,
            "industry": job_description.industry,
            "requirements": [req.dict() for req in job_description.requirements]
        }
    
    def _convert_to_evaluation_object(
        self,
        evaluation_data: Dict[str, Any],
        candidate_facts: CandidateFacts,
        job_description: JobDescription,
        github_analysis: List[RepositoryAnalysis]
    ) -> CandidateEvaluation:
        """Convert evaluation data to CandidateEvaluation object."""
        
        # extract basic information
        candidate_name = candidate_facts.candidate.full_name or "Unknown"
        overall_score = evaluation_data.get("overall_score", 0.0)
        probability_fit = evaluation_data.get("probability_fit", 0.0)
        
        # create skill matches
        skill_matches = []
        for skill_match_data in evaluation_data.get("skill_matches", []):
            skill_matches.append(SkillMatch(
                skill=skill_match_data.get("skill", ""),
                required=skill_match_data.get("required", False),
                candidate_has=skill_match_data.get("candidate_has", False),
                match_score=skill_match_data.get("match_score", 0.0),
                evidence=skill_match_data.get("evidence", [])
            ))
        
        # create evaluation categories
        categories = []
        for cat_data in evaluation_data.get("categories", []):
            categories.append(EvaluationCategory(
                category=cat_data.get("category", ""),
                score=cat_data.get("score", 0.0),
                weight=cat_data.get("weight", 0.0),
                weighted_score=cat_data.get("weighted_score", 0.0),
                details=cat_data.get("details", []),
                strengths=cat_data.get("strengths", []),
                weaknesses=cat_data.get("weaknesses", [])
            ))
        
        return CandidateEvaluation(
            candidate_name=candidate_name,
            job_title=job_description.title,
            overall_score=overall_score,
            probability_fit=probability_fit,
            categories=categories,
            skill_matches=skill_matches,
            relevant_repositories=github_analysis,
            key_strengths=evaluation_data.get("key_strengths", []),
            key_concerns=evaluation_data.get("key_concerns", []),
            recommendations=evaluation_data.get("recommendations", []),
            evaluation_reasoning=evaluation_data.get("evaluation_reasoning", ""),
            confidence_level=evaluation_data.get("confidence_level", "medium")
        )
    
    def _save_evaluation_results(self, evaluation: CandidateEvaluation) -> None:
        """Save evaluation results to file."""
        
        # create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"candidate_evaluation_{evaluation.candidate_name.replace(' ', '_')}_{timestamp}.json"
        filepath = output_dir / filename
        
        # save evaluation results
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(evaluation.dict(), f, indent=2, ensure_ascii=False)
        
        print(f"💾 Evaluation results saved to: {filepath}")
    
    def get_evaluation_summary(self, evaluation: CandidateEvaluation) -> str:
        """Generate a human-readable evaluation summary."""
        
        summary = f"""
============================================================
CANDIDATE EVALUATION SUMMARY
============================================================

🎯 Candidate: {evaluation.candidate_name}
📋 Position: {evaluation.job_title}
📊 Overall Score: {evaluation.overall_score:.1f}/100
🎲 Probability of Fit: {evaluation.probability_fit:.1%}
🔍 Confidence Level: {evaluation.confidence_level.title()}

📈 CATEGORY BREAKDOWN:
"""
        
        for category in evaluation.categories:
            summary += f"  • {category.category}: {category.score:.1f}/100 (Weight: {category.weight:.1f})\n"
        
        summary += f"""
💪 KEY STRENGTHS:
"""
        for strength in evaluation.key_strengths:
            summary += f"  • {strength}\n"
        
        if evaluation.key_concerns:
            summary += f"""
⚠️ KEY CONCERNS:
"""
            for concern in evaluation.key_concerns:
                summary += f"  • {concern}\n"
        
        summary += f"""
💡 RECOMMENDATIONS:
"""
        for i, rec in enumerate(evaluation.recommendations, 1):
            summary += f"  {i}. {rec}\n"
        
        summary += f"""
🔍 DETAILED REASONING:
{evaluation.evaluation_reasoning}

============================================================
"""
        
        return summary
