"""Assessment generation tool for creating comprehensive candidate evaluations."""

from typing import Any, Optional, List, Dict

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input

from utils.schemas import JobDescription, RepositoryAnalysis, CandidateFacts
from agents.github_agent import GitHubProfileData
from tools.ai_evaluator import AIEvaluator
from tools.skills_extractor import SkillsExtractor


class AssessmentGenerator:
    """Tool for generating comprehensive candidate assessments and recommendations."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
        self.ai_evaluator = AIEvaluator()
        self.skills_extractor = SkillsExtractor()
    
    def generate_comprehensive_assessment_with_info(
        self, 
        candidate_info: dict, 
        job_description: JobDescription,
        github_analysis: Optional[GitHubProfileData],
        relevant_repos: List[RepositoryAnalysis],
        code_analysis: Dict[str, Any],
        skill_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive assessment and recommendations using AI-powered evaluation."""
        
        print("🤖 Starting AI-powered comprehensive assessment...")
        
        # extract skills from resume and GitHub data
        resume_skills = self.skills_extractor.extract_skills_from_resume(
            candidate_info.get('resume_text', '')
        )
        
        github_skills = self.skills_extractor.extract_skills_from_github(
            github_analysis.dict() if github_analysis else {}
        )
        
        # combine skills
        combined_skills = self.skills_extractor.combine_skills(resume_skills, github_skills)
        
        # perform AI-powered evaluation
        try:
            llm = self.portia.config.get_generative_model("google/gemini-2.0-flash")
        except:
            try:
                llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
            except:
                llm = self.portia.config.get_generative_model("google/gemini-1.0-pro")
        
        ai_evaluation = self.ai_evaluator.evaluate_candidate(
            job_description=job_description.dict(),
            resume_data=candidate_info,
            github_data=github_analysis.dict() if github_analysis else {},
            skills_data=combined_skills.dict(),
            llm=llm
        )
        
        # create comprehensive assessment result
        assessment_result = {
            "overall_assessment": ai_evaluation.technical_assessment,
            "recommendations": ai_evaluation.recommendations,
            "match_score": self._normalize_score(ai_evaluation.overall_score),
            "score_breakdown": {
                "skill_match": {
                    "score": self._normalize_score(ai_evaluation.skill_match_score),
                    "reasoning": ai_evaluation.skill_match_reasoning
                },
                "experience_relevance": {
                    "score": self._normalize_score(ai_evaluation.experience_relevance_score),
                    "reasoning": ai_evaluation.experience_reasoning
                },
                "github_activity": {
                    "score": self._normalize_score(ai_evaluation.github_activity_score),
                    "reasoning": ai_evaluation.github_reasoning
                },
                "code_quality": {
                    "score": self._normalize_score(ai_evaluation.code_quality_score),
                    "reasoning": ai_evaluation.code_quality_reasoning
                }
            },
            "strengths": ai_evaluation.strengths,
            "weaknesses": ai_evaluation.weaknesses,
            "cultural_fit": ai_evaluation.cultural_fit,
            "final_recommendation": ai_evaluation.final_recommendation,
            "detected_skills": combined_skills.dict(),
            "scoring_criteria": self._get_scoring_criteria()
        }
        
        return assessment_result
    
    def generate_comprehensive_assessment(
        self, 
        candidate_facts: CandidateFacts, 
        job_description: JobDescription,
        github_analysis: Optional[GitHubProfileData],
        relevant_repos: List[RepositoryAnalysis],
        code_analysis: Dict[str, Any],
        skill_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive assessment and recommendations with intelligent scoring."""
        
        # calculate intelligent match score
        score_breakdown = self._calculate_intelligent_match_score(
            candidate_facts, job_description, github_analysis, 
            relevant_repos, code_analysis, skill_matches
        )
        overall_score = score_breakdown["overall_score"]
        
        # generate assessment
        assessment = self._create_assessment_plan()
        result = self.portia.run_plan(assessment, plan_run_inputs={
            "candidate_data": self._convert_candidate_facts_to_dict(candidate_facts),
            "job_requirements": job_description.dict(),
            "skill_matches": skill_matches,
            "github_analysis": github_analysis.dict() if github_analysis else {},
            "relevant_repos": [repo.dict() for repo in relevant_repos],
            "code_analysis": code_analysis
        })
        
        # get the final output which should contain the assessment
        if result.outputs.final_output:
            assessment_data = result.outputs.final_output.get_value()
        else:
            # fallback: get the last step output
            step_outputs = list(result.outputs.step_outputs.values())
            assessment_data = step_outputs[-1].get_value() if step_outputs else {}
        
        # handle the case where assessment_data is a string
        if isinstance(assessment_data, str):
            # extract assessment from text
            return self._extract_assessment_from_text(assessment_data, overall_score)
        
        # ensure assessment_data is a dictionary
        if not isinstance(assessment_data, dict):
            assessment_data = {}
        
        return {
            "overall_assessment": assessment_data.get("overall_assessment", "Assessment completed"),
            "recommendations": assessment_data.get("recommendations", []),
            "match_score": overall_score,
            "score_breakdown": {
                "scoring_criteria": self._get_scoring_criteria()
            }
        }
    
    def _calculate_intelligent_match_score_with_info(
        self,
        candidate_info: dict,
        job_description: JobDescription,
        github_analysis: Optional[GitHubProfileData],
        relevant_repos: List[RepositoryAnalysis],
        code_analysis: Dict[str, Any],
        skill_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate intelligent overall match score based on multiple factors using candidate info."""
        
        # 1. Skill Match Score (40% weight)
        skill_score = self._calculate_skill_match_component(skill_matches)
        
        # 2. GitHub Activity Score (25% weight)
        github_score = self._calculate_github_activity_component(github_analysis)
        
        # 3. Repository Relevance Score (20% weight)
        repo_score = self._calculate_repository_relevance_component(relevant_repos, job_description)
        
        # 4. Code Quality Score (15% weight)
        code_score = self._calculate_code_quality_component(code_analysis)
        
        # calculate weighted overall score
        overall_score = (
            skill_score * 0.40 +
            github_score * 0.25 +
            repo_score * 0.20 +
            code_score * 0.15
        )
        
        # return detailed scoring breakdown
        return {
            "overall_score": min(overall_score, 1.0),
            "component_scores": {
                "skill_match": {
                    "score": skill_score,
                    "weight": 0.40,
                    "weighted_score": skill_score * 0.40,
                    "description": "Skills alignment with job requirements"
                },
                "github_activity": {
                    "score": github_score,
                    "weight": 0.25,
                    "weighted_score": github_score * 0.25,
                    "description": "GitHub activity and contributions"
                },
                "repository_relevance": {
                    "score": repo_score,
                    "weight": 0.20,
                    "weighted_score": repo_score * 0.20,
                    "description": "Repository relevance to job requirements"
                },
                "code_quality": {
                    "score": code_score,
                    "weight": 0.15,
                    "weighted_score": code_score * 0.15,
                    "description": "Code quality and best practices"
                }
            },
            "total_weighted_score": min(overall_score, 1.0)
        }
    
    def _calculate_intelligent_match_score(
        self,
        candidate_facts: CandidateFacts,
        job_description: JobDescription,
        github_analysis: Optional[GitHubProfileData],
        relevant_repos: List[RepositoryAnalysis],
        code_analysis: Dict[str, Any],
        skill_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate intelligent overall match score based on multiple factors."""
        
        # 1. Skill Match Score (40% weight)
        skill_score = self._calculate_skill_match_component(skill_matches)
        
        # 2. GitHub Activity Score (25% weight)
        github_score = self._calculate_github_activity_component(github_analysis)
        
        # 3. Repository Relevance Score (20% weight)
        repo_score = self._calculate_repository_relevance_component(relevant_repos, job_description)
        
        # 4. Code Quality Score (15% weight)
        code_score = self._calculate_code_quality_component(code_analysis)
        
        # calculate weighted overall score
        overall_score = (
            skill_score * 0.40 +
            github_score * 0.25 +
            repo_score * 0.20 +
            code_score * 0.15
        )
        
        # return detailed scoring breakdown
        return {
            "overall_score": min(overall_score, 1.0),
            "component_scores": {
                "skill_match": {
                    "score": skill_score,
                    "weight": 0.40,
                    "weighted_score": skill_score * 0.40,
                    "description": "Skills alignment with job requirements"
                },
                "github_activity": {
                    "score": github_score,
                    "weight": 0.25,
                    "weighted_score": github_score * 0.25,
                    "description": "GitHub activity and contributions"
                },
                "repository_relevance": {
                    "score": repo_score,
                    "weight": 0.20,
                    "weighted_score": repo_score * 0.20,
                    "description": "Repository relevance to job requirements"
                },
                "code_quality": {
                    "score": code_score,
                    "weight": 0.15,
                    "weighted_score": code_score * 0.15,
                    "description": "Code quality and best practices"
                }
            },
            "total_weighted_score": min(overall_score, 1.0)
        }
    
    def _calculate_skill_match_component(self, skill_matches: List[Dict[str, Any]]) -> float:
        """Calculate skill match component score."""
        
        if not skill_matches:
            return 0.0
        
        required_matches = [m for m in skill_matches if m["required"]]
        preferred_matches = [m for m in skill_matches if not m["required"]]
        
        # calculate required skills score (70% weight)
        required_score = 0.0
        if required_matches:
            required_hits = sum(1 for m in required_matches if m["candidate_has"])
            required_score = required_hits / len(required_matches)
        
        # calculate preferred skills score (30% weight)
        preferred_score = 0.0
        if preferred_matches:
            preferred_hits = sum(1 for m in preferred_matches if m["candidate_has"])
            preferred_score = preferred_hits / len(preferred_matches)
        
        return (required_score * 0.7) + (preferred_score * 0.3)
    
    def _calculate_github_activity_component(self, github_analysis: Optional[GitHubProfileData]) -> float:
        """Calculate GitHub activity component score."""
        
        if not github_analysis or not github_analysis.contributions:
            return 0.0
        
        total_contributions = github_analysis.contributions.total_contributions
        total_commits = github_analysis.contributions.total_commits
        active_days = github_analysis.contributions.active_days
        
        # scoring based on activity levels
        if total_contributions > 1000 and total_commits > 500 and active_days > 200:
            return 1.0  # exceptional activity
        elif total_contributions > 500 and total_commits > 200 and active_days > 100:
            return 0.9  # high activity
        elif total_contributions > 200 and total_commits > 100 and active_days > 50:
            return 0.7  # good activity
        elif total_contributions > 100 and total_commits > 50 and active_days > 25:
            return 0.5  # moderate activity
        elif total_contributions > 50 and total_commits > 20 and active_days > 10:
            return 0.3  # low activity
        else:
            return 0.1  # minimal activity
    
    def _calculate_repository_relevance_component(self, relevant_repos: List[RepositoryAnalysis], job_description: JobDescription) -> float:
        """Calculate repository relevance component score."""
        
        if not relevant_repos:
            return 0.0
        
        # calculate average relevance score
        avg_relevance = sum(repo.relevance_score for repo in relevant_repos) / len(relevant_repos)
        
        # bonus for number of relevant repos (up to 5 repos)
        repo_count_bonus = min(len(relevant_repos) / 5.0, 1.0) * 0.2
        
        # bonus for high relevance repos
        high_relevance_bonus = sum(0.1 for repo in relevant_repos if repo.relevance_score > 0.8)
        
        return min(avg_relevance + repo_count_bonus + high_relevance_bonus, 1.0)
    
    def _calculate_code_quality_component(self, code_analysis: Dict[str, Any]) -> float:
        """Calculate code quality component score."""
        
        if not code_analysis:
            return 0.0
        
        score = 0.0
        
        # languages found (up to 30%)
        languages_found = code_analysis.get("languages_found", [])
        if languages_found:
            score += min(len(languages_found) / 5.0, 1.0) * 0.3
        
        # frameworks detected (up to 30%)
        frameworks_detected = code_analysis.get("frameworks_detected", [])
        if frameworks_detected:
            score += min(len(frameworks_detected) / 3.0, 1.0) * 0.3
        
        # code quality indicators (up to 40%)
        quality_indicators = code_analysis.get("code_quality_indicators", [])
        if quality_indicators:
            score += min(len(quality_indicators) / 3.0, 1.0) * 0.4
        
        return score
    
    def _extract_assessment_from_text(self, text: str, match_score: float, score_breakdown: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract assessment information from LLM text output."""
        
        # simple extraction based on common patterns
        overall_assessment = "Assessment completed based on available data"
        recommendations = []
        
        # look for assessment patterns
        if "strong candidate" in text.lower() or "good fit" in text.lower():
            overall_assessment = "Strong candidate with good technical alignment"
        elif "moderate" in text.lower() or "average" in text.lower():
            overall_assessment = "Moderate candidate with some relevant experience"
        elif "weak" in text.lower() or "poor fit" in text.lower():
            overall_assessment = "Weak candidate with limited relevant experience"
        
        # extract recommendations
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # remove bullet points and numbers
                clean_line = line.lstrip('-•*1234567890. ')
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)
        
        # if no recommendations found, add some generic ones
        if not recommendations:
            if match_score > 0.7:
                recommendations = ["Candidate shows strong potential for the role"]
            elif match_score > 0.4:
                recommendations = ["Consider additional training or mentorship"]
            else:
                recommendations = ["May need significant upskilling for this role"]
        
        result = {
            "overall_assessment": overall_assessment,
            "recommendations": recommendations[:5],  # limit to 5 recommendations
            "match_score": match_score
        }
        
        if score_breakdown:
            result["score_breakdown"] = score_breakdown
            
        return result
    
    def _create_assessment_plan(self) -> PlanBuilderV2:
        """Create a plan for generating comprehensive assessment."""
        
        plan = PlanBuilderV2(label="Generate candidate assessment")
        
        # define inputs
        plan.input(name="candidate_data", description="Candidate information")
        plan.input(name="job_requirements", description="Job requirements")
        plan.input(name="skill_matches", description="Skill matching results")
        plan.input(name="github_analysis", description="GitHub analysis")
        plan.input(name="relevant_repos", description="Relevant repositories")
        plan.input(name="code_analysis", description="Code analysis results")
        
        plan.llm_step(
            task="Analyze how well the candidate fits the job requirements based on all available data and provide a comprehensive assessment with recommendations",
            inputs=[
                Input("candidate_data"),
                Input("job_requirements"),
                Input("skill_matches"),
                Input("github_analysis"),
                Input("relevant_repos"),
                Input("code_analysis")
            ]
        )
        
        return plan.build()
    
    def _convert_candidate_facts_to_dict(self, candidate_facts: CandidateFacts) -> dict:
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

    def _normalize_score(self, score: float) -> float:
        """Normalize score to ensure it's between 0 and 1 (0-100%)."""
        
        # if score is already between 0 and 1, return as is
        if 0 <= score <= 1:
            return score
        
        # if score is between 1 and 100, convert to decimal
        if 1 < score <= 100:
            return score / 100.0
        
        # if score is greater than 100, cap it at 1.0
        if score > 100:
            return 1.0
        
        # if score is negative, return 0
        return 0.0
    
    def _get_scoring_criteria(self) -> Dict[str, Any]:
        """Get transparent scoring criteria for HR understanding."""
        
        return {
            "overview": "Candidate evaluation is based on a comprehensive scoring system that assesses multiple dimensions of technical and professional fit.",
            "scoring_components": {
                "skill_match": {
                    "weight": "40%",
                    "description": "How well the candidate's technical skills align with job requirements",
                    "criteria": [
                        "Required skills match (70% of skill score)",
                        "Preferred skills match (30% of skill score)",
                        "Skill depth and proficiency level",
                        "Relevance to the specific role"
                    ],
                    "scoring_scale": {
                        "90-100%": "Excellent skill alignment with all required skills",
                        "80-89%": "Strong skill alignment with most required skills",
                        "70-79%": "Good skill alignment with some gaps",
                        "60-69%": "Moderate skill alignment with significant gaps",
                        "Below 60%": "Poor skill alignment with major gaps"
                    }
                },
                "experience_relevance": {
                    "weight": "25%",
                    "description": "Relevance of work experience to the job requirements",
                    "criteria": [
                        "Industry experience relevance",
                        "Role responsibility alignment",
                        "Project complexity and scope",
                        "Technology stack overlap"
                    ],
                    "scoring_scale": {
                        "90-100%": "Highly relevant experience in similar roles",
                        "80-89%": "Relevant experience with good transferability",
                        "70-79%": "Some relevant experience with gaps",
                        "60-69%": "Limited relevant experience",
                        "Below 60%": "Minimal relevant experience"
                    }
                },
                "github_activity": {
                    "weight": "20%",
                    "description": "GitHub activity and open source contributions",
                    "criteria": [
                        "Repository activity and contributions",
                        "Code quality and best practices",
                        "Collaboration and community engagement",
                        "Project complexity and relevance"
                    ],
                    "scoring_scale": {
                        "90-100%": "Exceptional GitHub activity with high-quality contributions",
                        "80-89%": "Strong GitHub activity with good contributions",
                        "70-79%": "Good GitHub activity with some quality projects",
                        "60-69%": "Moderate GitHub activity",
                        "Below 60%": "Limited GitHub activity"
                    }
                },
                "code_quality": {
                    "weight": "15%",
                    "description": "Code quality and technical best practices",
                    "criteria": [
                        "Code organization and structure",
                        "Documentation quality",
                        "Testing practices",
                        "Performance considerations"
                    ],
                    "scoring_scale": {
                        "90-100%": "Excellent code quality with best practices",
                        "80-89%": "Good code quality with some best practices",
                        "70-79%": "Acceptable code quality",
                        "60-69%": "Basic code quality",
                        "Below 60%": "Poor code quality"
                    }
                }
            },
            "overall_score_interpretation": {
                "90-100%": "Exceptional candidate - Strongly recommend for interview",
                "80-89%": "Strong candidate - Recommend for interview",
                "70-79%": "Good candidate - Consider for interview with reservations",
                "60-69%": "Moderate candidate - Consider for junior role or with training",
                "Below 60%": "Weak candidate - Not recommended for this role"
            },
            "transparency_notes": [
                "All scores are calculated using objective criteria and AI analysis",
                "Scores are normalized to ensure consistency across evaluations",
                "Final recommendations consider both technical and cultural fit",
                "HR can review detailed reasoning for each scoring component",
                "Scores are meant to guide decisions, not replace human judgment"
            ]
        }
