"""AI-Powered Candidate Evaluator Tool for intelligent assessment."""

import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class AIEvaluationResult(BaseModel):
    """Result of AI-powered candidate evaluation."""
    
    overall_score: float = Field(description="Overall match score (0-100)")
    skill_match_score: float = Field(description="Skills alignment score (0-100)")
    experience_relevance_score: float = Field(description="Experience relevance score (0-100)")
    github_activity_score: float = Field(description="GitHub activity and quality score (0-100)")
    code_quality_score: float = Field(description="Code quality assessment score (0-100)")
    
    skill_match_reasoning: str = Field(description="Detailed reasoning for skill match")
    experience_reasoning: str = Field(description="Detailed reasoning for experience relevance")
    github_reasoning: str = Field(description="Detailed reasoning for GitHub assessment")
    code_quality_reasoning: str = Field(description="Detailed reasoning for code quality")
    
    strengths: List[str] = Field(description="Candidate's key strengths", default_factory=list)
    weaknesses: List[str] = Field(description="Areas for improvement", default_factory=list)
    recommendations: List[str] = Field(description="Specific recommendations", default_factory=list)
    
    technical_assessment: str = Field(description="Overall technical assessment")
    cultural_fit: str = Field(description="Cultural fit assessment")
    final_recommendation: str = Field(description="Final hiring recommendation")


class AIEvaluator:
    """AI-powered tool for evaluating candidates using job description, resume, and GitHub data."""
    
    def __init__(self, llm_model: str = "google/gemini-2.0-flash"):
        self.llm_model = llm_model
    
    def evaluate_candidate(
        self,
        job_description: Dict[str, Any],
        resume_data: Dict[str, Any],
        github_data: Dict[str, Any],
        skills_data: Dict[str, Any],
        llm=None
    ) -> AIEvaluationResult:
        """Evaluate candidate using AI-powered analysis."""
        
        print("🤖 Performing AI-powered candidate evaluation...")
        
        # prepare comprehensive evaluation prompt
        prompt = self._create_evaluation_prompt(job_description, resume_data, github_data, skills_data)
        
        try:
            # call LLM for evaluation
            from portia.model import Message
            message = Message(role="user", content=prompt)
            response = llm.get_response([message])
            
            # parse the response
            evaluation_data = self._parse_evaluation_response(response.content)
            
            return AIEvaluationResult(**evaluation_data)
            
        except Exception as e:
            print(f"❌ Error in AI evaluation: {str(e)}")
            # return default evaluation
            return self._create_default_evaluation()
    
    def _create_evaluation_prompt(
        self,
        job_description: Dict[str, Any],
        resume_data: Dict[str, Any],
        github_data: Dict[str, Any],
        skills_data: Dict[str, Any]
    ) -> str:
        """Create comprehensive evaluation prompt."""
        
        return f"""
You are an experienced technical recruiting manager with 10+ years of experience in hiring software engineers. Your task is to evaluate a candidate for a technical position using comprehensive data from their resume, GitHub profile, and skills analysis.

**JOB DESCRIPTION:**
Title: {job_description.get('title', 'Unknown')}
Company: {job_description.get('company', 'Unknown')}
Required Skills: {job_description.get('required_skills', [])}
Preferred Skills: {job_description.get('preferred_skills', [])}
Experience Level: {job_description.get('experience_level', 'Unknown')}
Role Type: {job_description.get('role_type', 'Unknown')}

**CANDIDATE RESUME DATA:**
Name: {resume_data.get('candidate_name', 'Unknown')}
Email: {resume_data.get('email', 'Unknown')}
Experience: {json.dumps(resume_data.get('experience', []), indent=2)}
Education: {json.dumps(resume_data.get('education', []), indent=2)}
Projects: {json.dumps(resume_data.get('projects', []), indent=2)}

**CANDIDATE GITHUB DATA:**
Profile: {github_data.get('profile_url', 'Unknown')}
Public Repos: {github_data.get('public_repos', 0)}
Followers: {github_data.get('followers', 0)}
Following: {github_data.get('following', 0)}
Total Contributions: {github_data.get('total_contributions', 0)}
Top Languages: {github_data.get('top_languages', [])}
Repositories: {json.dumps(github_data.get('repositories', [])[:5], indent=2)}  # Top 5 repos

**DETECTED SKILLS:**
Programming Languages: {skills_data.get('programming_languages', [])}
Frameworks: {skills_data.get('frameworks', [])}
Databases: {skills_data.get('databases', [])}
Cloud Platforms: {skills_data.get('cloud_platforms', [])}
Tools: {skills_data.get('tools', [])}
Methodologies: {skills_data.get('methodologies', [])}
Soft Skills: {skills_data.get('soft_skills', [])}
Total Skills: {skills_data.get('skill_count', 0)}

**EVALUATION INSTRUCTIONS:**

As a technical recruiting manager, provide a comprehensive evaluation with the following criteria:

1. **SKILL MATCH (0-100)**: How well do the candidate's skills align with job requirements?
   - Consider both required and preferred skills
   - Evaluate skill depth and breadth
   - Factor in skill relevance to the role

2. **EXPERIENCE RELEVANCE (0-100)**: How relevant is their work experience?
   - Match experience to job requirements
   - Consider industry relevance
   - Evaluate role progression and responsibilities

3. **GITHUB ACTIVITY (0-100)**: How active and engaged are they in open source?
   - Repository activity and contributions
   - Code quality indicators
   - Community engagement (followers, following)
   - Project complexity and relevance

4. **CODE QUALITY (0-100)**: What's the quality of their code and projects?
   - Repository structure and organization
   - Documentation quality
   - Project complexity and scope
   - Best practices implementation

**EVALUATION REQUIREMENTS:**

Provide your evaluation in EXACTLY this JSON format:

{{
    "overall_score": 85.5,
    "skill_match_score": 90.0,
    "experience_relevance_score": 85.0,
    "github_activity_score": 80.0,
    "code_quality_score": 85.0,
    
    "skill_match_reasoning": "Detailed explanation of skill alignment with specific examples...",
    "experience_reasoning": "Detailed explanation of experience relevance with specific examples...",
    "github_reasoning": "Detailed explanation of GitHub activity assessment with specific examples...",
    "code_quality_reasoning": "Detailed explanation of code quality assessment with specific examples...",
    
    "strengths": ["Strong Python skills", "Good GitHub activity", "Relevant experience"],
    "weaknesses": ["Limited cloud experience", "Could improve documentation"],
    "recommendations": ["Consider for interview", "Ask about cloud projects"],
    
    "technical_assessment": "Overall technical assessment summary...",
    "cultural_fit": "Cultural fit assessment...",
    "final_recommendation": "Final hiring recommendation with reasoning..."
}}

**EVALUATION GUIDELINES:**

- Be thorough but fair in your assessment
- Provide specific examples from the candidate's data
- Consider both technical and soft skills
- Evaluate potential for growth and learning
- Be honest about limitations and areas for improvement
- Provide actionable recommendations
- Consider the role requirements and company needs

**IMPORTANT:** Return ONLY the JSON object. Do not include any additional text or explanations outside the JSON structure.
"""
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM response into structured evaluation data."""
        
        try:
            # find JSON in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                evaluation_data = json.loads(json_str)
                
                # validate required fields
                required_fields = [
                    'overall_score', 'skill_match_score', 'experience_relevance_score',
                    'github_activity_score', 'code_quality_score'
                ]
                
                for field in required_fields:
                    if field not in evaluation_data:
                        evaluation_data[field] = 0.0
                
                return evaluation_data
            else:
                print("⚠️ No JSON found in LLM response, using default evaluation")
                return self._create_default_evaluation_dict()
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing JSON response: {str(e)}")
            return self._create_default_evaluation_dict()
        except Exception as e:
            print(f"⚠️ Error parsing evaluation response: {str(e)}")
            return self._create_default_evaluation_dict()
    
    def _create_default_evaluation_dict(self) -> Dict[str, Any]:
        """Create default evaluation data structure."""
        
        return {
            "overall_score": 50.0,
            "skill_match_score": 50.0,
            "experience_relevance_score": 50.0,
            "github_activity_score": 50.0,
            "code_quality_score": 50.0,
            
            "skill_match_reasoning": "Unable to perform detailed skill analysis due to parsing issues.",
            "experience_reasoning": "Unable to perform detailed experience analysis due to parsing issues.",
            "github_reasoning": "Unable to perform detailed GitHub analysis due to parsing issues.",
            "code_quality_reasoning": "Unable to perform detailed code quality analysis due to parsing issues.",
            
            "strengths": ["Data available for analysis"],
            "weaknesses": ["Limited data for comprehensive assessment"],
            "recommendations": ["Consider manual review of candidate materials"],
            
            "technical_assessment": "Unable to provide comprehensive technical assessment due to data parsing issues.",
            "cultural_fit": "Unable to assess cultural fit due to limited data.",
            "final_recommendation": "Recommend manual review of candidate materials for proper assessment."
        }
    
    def _create_default_evaluation(self) -> AIEvaluationResult:
        """Create default evaluation result."""
        
        return AIEvaluationResult(**self._create_default_evaluation_dict())
