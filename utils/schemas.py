from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class _lower:
    """small caps marker"""


class Contact(BaseModel):
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: List[str] = Field(default_factory=list)
    portfolio: List[str] = Field(default_factory=list)
    other_links: List[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    school: str
    degree: str
    start: Optional[str] = None
    end: Optional[str] = None


class ExperienceEntry(BaseModel):
    company: str
    role: str
    start: Optional[str] = None
    end: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str
    link: Optional[str] = None
    description: Optional[str] = None
    tech: List[str] = Field(default_factory=list)


class Skills(BaseModel):
    primary: List[str] = Field(default_factory=list)
    secondary: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CandidateFacts(BaseModel):
    request_id: str
    candidate: Contact
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: List[ProjectEntry] = Field(default_factory=list)
    parse_warnings: List[str] = Field(default_factory=list)

    model_config = {
        "extra": "forbid",
    }


# Job Description schemas
class JobRequirement(BaseModel):
    """Individual job requirement."""
    requirement: str = Field(description="The specific requirement")
    category: str = Field(description="Category: skills, experience, education, etc.")
    importance: str = Field(description="Importance level: required, preferred, nice_to_have")
    weight: float = Field(description="Weight for scoring (0-1)", default=1.0)


class JobDescription(BaseModel):
    """Parsed job description data."""
    title: str = Field(description="Job title")
    company: Optional[str] = Field(description="Company name", default=None)
    location: Optional[str] = Field(description="Job location", default=None)
    description: str = Field(description="Full job description")
    
    # Parsed requirements
    required_skills: List[str] = Field(description="Required technical skills", default_factory=list)
    preferred_skills: List[str] = Field(description="Preferred technical skills", default_factory=list)
    required_experience: List[str] = Field(description="Required experience areas", default_factory=list)
    preferred_experience: List[str] = Field(description="Preferred experience areas", default_factory=list)
    technologies: List[str] = Field(description="Technologies mentioned", default_factory=list)
    frameworks: List[str] = Field(description="Frameworks mentioned", default_factory=list)
    
    # Requirements with weights
    requirements: List[JobRequirement] = Field(description="Detailed requirements with weights", default_factory=list)
    
    # Role characteristics
    role_type: str = Field(description="Role type: frontend, backend, fullstack, etc.", default="")
    seniority_level: str = Field(description="Seniority: junior, mid, senior, lead", default="")
    industry: Optional[str] = Field(description="Industry focus", default=None)


# Candidate Evaluation schemas
class SkillMatch(BaseModel):
    """Skill matching result."""
    skill: str = Field(description="Skill name")
    required: bool = Field(description="Whether this skill is required")
    candidate_has: bool = Field(description="Whether candidate has this skill")
    match_score: float = Field(description="Match score (0-1)")
    evidence: List[str] = Field(description="Evidence of skill from resume/GitHub", default_factory=list)


class RepositoryAnalysis(BaseModel):
    """Analysis of a specific repository."""
    name: str = Field(description="Repository name")
    url: str = Field(description="Repository URL")
    relevance_score: float = Field(description="Relevance to job (0-1)")
    languages_used: List[str] = Field(description="Languages used", default_factory=list)
    frameworks_detected: List[str] = Field(description="Frameworks detected", default_factory=list)
    code_quality_indicators: List[str] = Field(description="Code quality indicators", default_factory=list)
    project_complexity: str = Field(description="Project complexity assessment")
    contribution_evidence: List[str] = Field(description="Evidence of contributions", default_factory=list)


class EvaluationCategory(BaseModel):
    """Evaluation category breakdown."""
    category: str = Field(description="Category name")
    score: float = Field(description="Score (0-100)")
    weight: float = Field(description="Weight in overall score")
    weighted_score: float = Field(description="Weighted score")
    details: List[str] = Field(description="Detailed breakdown", default_factory=list)
    strengths: List[str] = Field(description="Strengths in this category", default_factory=list)
    weaknesses: List[str] = Field(description="Areas for improvement", default_factory=list)


class CandidateEvaluation(BaseModel):
    """Complete candidate evaluation result."""
    candidate_name: str = Field(description="Candidate name")
    job_title: str = Field(description="Job title being evaluated for")
    overall_score: float = Field(description="Overall suitability score (0-100)")
    probability_fit: float = Field(description="Probability of being a good fit (0-1)")
    
    # Detailed breakdown
    categories: List[EvaluationCategory] = Field(description="Category breakdowns", default_factory=list)
    skill_matches: List[SkillMatch] = Field(description="Skill matching results", default_factory=list)
    relevant_repositories: List[RepositoryAnalysis] = Field(description="Relevant repository analysis", default_factory=list)
    
    # Summary
    key_strengths: List[str] = Field(description="Key strengths", default_factory=list)
    key_concerns: List[str] = Field(description="Key concerns", default_factory=list)
    recommendations: List[str] = Field(description="Recommendations", default_factory=list)
    
    # Transparency
    evaluation_reasoning: str = Field(description="Detailed reasoning for the score")
    confidence_level: str = Field(description="Confidence in evaluation: high, medium, low")


# GitHub-related schemas
class GitHubContributionData(BaseModel):
    """GitHub contribution data."""
    total_contributions: int = Field(description="Total contributions in calendar", default=0)
    total_commits: int = Field(description="Total commit contributions", default=0)
    total_prs: int = Field(description="Total pull request contributions", default=0)
    total_reviews: int = Field(description="Total pull request review contributions", default=0)
    active_days: int = Field(description="Number of active contribution days", default=0)
    contribution_calendar: List[Dict[str, Any]] = Field(description="Contribution calendar data", default_factory=list)


class GitHubRepositoryData(BaseModel):
    """GitHub repository data."""
    name: str = Field(description="Repository name")
    description: str = Field(description="Repository description", default="")
    url: str = Field(description="Repository URL")
    languages: List[str] = Field(description="Programming languages used", default_factory=list)
    stars: int = Field(description="Number of stars", default=0)
    forks: int = Field(description="Number of forks", default=0)
    last_updated: str = Field(description="Last update date", default="")
    relevance_score: float = Field(description="Relevance score (0-1)", default=0.0)


class GitHubProfileData(BaseModel):
    """Comprehensive GitHub profile data."""
    username: str = Field(description="GitHub username")
    profile_url: str = Field(description="Full GitHub profile URL")
    is_valid_url: bool = Field(description="Whether the URL is valid")
    
    # Profile information
    name: Optional[str] = Field(description="Full name from profile", default=None)
    bio: Optional[str] = Field(description="Profile bio", default=None)
    location: Optional[str] = Field(description="Location", default=None)
    company: Optional[str] = Field(description="Company", default=None)
    email: Optional[str] = Field(description="Email", default=None)
    website: Optional[str] = Field(description="Website", default=None)
    
    # Activity metrics
    public_repos: int = Field(description="Number of public repositories", default=0)
    followers: int = Field(description="Number of followers", default=0)
    following: int = Field(description="Number of following", default=0)
    account_created: Optional[str] = Field(description="Account creation date", default=None)
    last_updated: Optional[str] = Field(description="Last activity date", default=None)
    
    # Analysis data
    contributions: Optional[GitHubContributionData] = Field(description="Contribution analysis", default=None)
    repositories: List[GitHubRepositoryData] = Field(description="List of repositories", default_factory=list)
    profile_summary: str = Field(description="Comprehensive profile summary", default="")
    
    # Errors and warnings
    scan_errors: List[str] = Field(description="Errors during scanning", default_factory=list)

