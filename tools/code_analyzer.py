"""Code analysis tool for analyzing repository code and patterns."""

from typing import Any, List, Dict

from utils.schemas import JobDescription, RepositoryAnalysis


class CodeAnalyzer:
    """Tool for analyzing code patterns and quality in repositories."""
    
    def __init__(self):
        pass
    
    def analyze_repository_code_deep(self, relevant_repos: List[RepositoryAnalysis], job_description: JobDescription, github_url: str, github_agent) -> Dict[str, Any]:
        """Perform deep code analysis on relevant repositories using enhanced GitHub agent."""
        
        if not relevant_repos:
            return {}
        
        print(f"🔍 Performing deep code analysis on {len(relevant_repos)} relevant repositories...")
        
        # get repository names for deep analysis
        repo_names = [repo.name for repo in relevant_repos]
        
        # use enhanced GitHub agent for deep code analysis
        deep_analysis = github_agent.analyze_specific_repositories(github_url, repo_names, job_description)
        
        # combine with basic analysis
        code_analysis = {
            "repositories_analyzed": len(relevant_repos),
            "languages_found": [],
            "frameworks_detected": [],
            "code_quality_indicators": [],
            "coding_patterns": [],
            "best_practices_followed": [],
            "deep_analysis": deep_analysis
        }
        
        # collect all languages and frameworks from basic analysis
        for repo in relevant_repos:
            code_analysis["languages_found"].extend(repo.languages_used)
            code_analysis["frameworks_detected"].extend(repo.frameworks_detected)
            code_analysis["code_quality_indicators"].extend(repo.code_quality_indicators)
        
        # remove duplicates
        code_analysis["languages_found"] = list(set(code_analysis["languages_found"]))
        code_analysis["frameworks_detected"] = list(set(code_analysis["frameworks_detected"]))
        code_analysis["code_quality_indicators"] = list(set(code_analysis["code_quality_indicators"]))
        
        # analyze coding patterns based on job requirements
        if "frontend" in job_description.role_type.lower():
            code_analysis["coding_patterns"] = self._analyze_frontend_patterns(relevant_repos)
        elif "backend" in job_description.role_type.lower():
            code_analysis["coding_patterns"] = self._analyze_backend_patterns(relevant_repos)
        
        return code_analysis
    
    def _analyze_frontend_patterns(self, repos: List[RepositoryAnalysis]) -> List[str]:
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
    
    def _analyze_backend_patterns(self, repos: List[RepositoryAnalysis]) -> List[str]:
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
