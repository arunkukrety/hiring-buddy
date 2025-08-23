"""Repository analysis tool for analyzing GitHub repositories."""

from typing import Any, Optional, List, Dict

from utils.schemas import JobDescription, RepositoryAnalysis
from agents.github_agent import GitHubProfileData


class RepositoryAnalyzer:
    """Tool for analyzing GitHub repositories and their relevance to job requirements."""
    
    def __init__(self):
        pass
    
    def identify_relevant_repositories(self, github_analysis: Optional[GitHubProfileData], job_description: JobDescription) -> List[RepositoryAnalysis]:
        """Identify repositories relevant to the job requirements."""
        
        if not github_analysis or not github_analysis.repositories:
            return []
        
        relevant_repos = []
        job_skills = set(job_description.required_skills + job_description.preferred_skills)
        job_technologies = set(job_description.technologies + job_description.frameworks)
        
        for repo in github_analysis.repositories:
            relevance_score = self._calculate_repository_relevance(repo, job_skills, job_technologies)
            
            if relevance_score > 0.2:  # only include moderately relevant repos
                repo_analysis = RepositoryAnalysis(
                    name=repo.name,
                    url=repo.url,
                    relevance_score=relevance_score,
                    languages_used=repo.languages,
                    frameworks_detected=self._detect_frameworks_in_repo(repo, job_description.frameworks),
                    code_quality_indicators=self._assess_repo_quality(repo),
                    project_complexity=self._assess_project_complexity(repo),
                    contribution_evidence=[f"Repository: {repo.name}"]
                )
                relevant_repos.append(repo_analysis)
        
        # sort by relevance score
        relevant_repos.sort(key=lambda x: x.relevance_score, reverse=True)
        return relevant_repos[:5]  # limit to top 5 most relevant
    
    def _calculate_repository_relevance(self, repo, job_skills: set, job_technologies: set) -> float:
        """Calculate how relevant a repository is to the job requirements."""
        
        score = 0.0
        
        # check languages
        repo_languages = set(repo.languages)
        language_overlap = len(repo_languages.intersection(job_technologies))
        if language_overlap > 0:
            score += 0.4 * (language_overlap / len(job_technologies))
        
        # check description for skill mentions
        description = repo.description.lower()
        for skill in job_skills:
            if skill.lower() in description:
                score += 0.3
        
        # boost score for active repositories
        if hasattr(repo, 'stars') and repo.stars > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _detect_frameworks_in_repo(self, repo, job_frameworks: List[str]) -> List[str]:
        """Detect frameworks used in the repository."""
        
        detected = []
        description = repo.description.lower()
        
        for framework in job_frameworks:
            if framework.lower() in description:
                detected.append(framework)
        
        return detected
    
    def _assess_repo_quality(self, repo) -> List[str]:
        """Assess repository quality indicators."""
        
        indicators = []
        
        if repo.description:
            indicators.append("Has description")
        
        if hasattr(repo, 'stars') and repo.stars > 0:
            indicators.append("Has community interest")
        
        return indicators
    
    def _assess_project_complexity(self, repo) -> str:
        """Assess project complexity level."""
        
        if hasattr(repo, 'stars') and repo.stars > 10:
            return "High complexity - Well-developed project"
        elif repo.description:
            return "Medium complexity - Substantial project"
        else:
            return "Low complexity - Simple project"
    
    def calculate_repository_relevance_component(self, relevant_repos: List[RepositoryAnalysis], job_description: JobDescription) -> float:
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
    
    def analyze_frontend_patterns(self, repos: List[RepositoryAnalysis]) -> List[str]:
        """Analyze frontend coding patterns."""
        
        patterns = []
        
        for repo in repos:
            if "JavaScript" in repo.languages_used:
                patterns.append("Uses modern JavaScript")
            if "CSS" in repo.languages_used:
                patterns.append("Implements styling")
            if "HTML" in repo.languages_used:
                patterns.append("Creates web interfaces")
            if any("React" in fw for fw in repo.frameworks_detected):
                patterns.append("Uses React framework")
            if any("Vue" in fw for fw in repo.frameworks_detected):
                patterns.append("Uses Vue framework")
            if any("Angular" in fw for fw in repo.frameworks_detected):
                patterns.append("Uses Angular framework")
        
        return list(set(patterns))
    
    def analyze_backend_patterns(self, repos: List[RepositoryAnalysis]) -> List[str]:
        """Analyze backend coding patterns."""
        
        patterns = []
        
        for repo in repos:
            if "Python" in repo.languages_used:
                patterns.append("Uses Python backend")
            if "Java" in repo.languages_used:
                patterns.append("Uses Java backend")
            if "Node.js" in repo.languages_used:
                patterns.append("Uses Node.js backend")
        
        return list(set(patterns))
