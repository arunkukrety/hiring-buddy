"""GitHub Agent for analyzing GitHub profiles and repositories."""

import os
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input

from utils.schemas import GitHubContributionData, GitHubRepositoryData, GitHubProfileData
from tools.github_scanner import GitHubScanner


class GitHubAgent:
    """Agent for analyzing GitHub profiles and repositories."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
        self.scanner = GitHubScanner()
    
    def analyze_github_profile(self, github_url: str) -> GitHubProfileData:
        """Analyze a GitHub profile and return comprehensive data."""
        
        print(f"🐙 Analyzing GitHub profile: {github_url}")
        
        if not self.scanner:
            print("⚠️ GitHub scanner not available")
            return self._create_empty_profile_data(github_url)
        
        try:
            # extract username from URL
            username = self._extract_username_from_url(github_url)
            if not username:
                print("❌ Could not extract username from GitHub URL")
                return self._create_empty_profile_data(github_url)
            
            # get comprehensive profile data
            profile_data = self.scanner.scan_profile_comprehensive(username)
            
            if profile_data:
                print(f"✅ Successfully analyzed GitHub profile for {username}")
                # convert dictionary to GitHubProfileData schema
                return self._convert_to_github_profile_data(profile_data, github_url)
            else:
                print("⚠️ No profile data returned from scanner")
                return self._create_empty_profile_data(github_url)
                
        except Exception as e:
            print(f"❌ Error analyzing GitHub profile: {str(e)}")
            return self._create_empty_profile_data(github_url)
    
    def get_comprehensive_profile(self, github_url: str) -> GitHubProfileData:
        """Get comprehensive GitHub profile data (enhanced method)."""
        return self.analyze_github_profile(github_url)
    
    def analyze_specific_repositories(self, github_url: str, repository_names: List[str], job_description) -> Dict[str, Any]:
        """Perform deep code analysis on specific repositories (enhanced method)."""
        
        username = self._extract_username_from_url(github_url)
        if not username or not self.scanner:
            print("⚠️ GitHub scanner not available for deep analysis")
            return {"error": "GitHub scanner not available"}
        
        try:
            print(f"🔍 Performing deep analysis on {len(repository_names)} repositories...")
            
            # use the scanner to analyze specific repositories
            analysis_results = {}
            
            for repo_name in repository_names:
                print(f"  📁 Analyzing repository: {repo_name}")
                
                # get repository details
                repo_data = self.scanner.get_repository_data(username, repo_name)
                if repo_data:
                    # analyze code patterns based on job requirements
                    code_analysis = self._analyze_repository_code_deep(repo_data, job_description)
                    analysis_results[repo_name] = {
                        "repository_data": repo_data,
                        "code_analysis": code_analysis
                    }
                else:
                    analysis_results[repo_name] = {"error": "Could not fetch repository data"}
            
            return {
                "repositories_analyzed": len(repository_names),
                "analysis_results": analysis_results,
                "summary": self._generate_analysis_summary(analysis_results, job_description)
            }
            
        except Exception as e:
            print(f"❌ Error in deep repository analysis: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _analyze_repository_code_deep(self, repo_data: Dict[str, Any], job_description) -> Dict[str, Any]:
        """Analyze repository code deeply based on job requirements."""
        
        analysis = {
            "languages_detected": [],
            "frameworks_detected": [],
            "code_quality_indicators": [],
            "coding_patterns": [],
            "best_practices": []
        }
        
        # detect languages
        if "languages" in repo_data:
            analysis["languages_detected"] = list(repo_data["languages"].keys())
        
        # detect frameworks based on job requirements
        if "description" in repo_data and repo_data["description"]:
            description_lower = repo_data["description"].lower()
            
            # check for frontend frameworks
            if "react" in description_lower:
                analysis["frameworks_detected"].append("React")
            if "vue" in description_lower:
                analysis["frameworks_detected"].append("Vue")
            if "angular" in description_lower:
                analysis["frameworks_detected"].append("Angular")
            if "tailwind" in description_lower:
                analysis["frameworks_detected"].append("Tailwind CSS")
            if "bootstrap" in description_lower:
                analysis["frameworks_detected"].append("Bootstrap")
        
        # analyze coding patterns based on job type
        if "frontend" in job_description.title.lower():
            analysis["coding_patterns"] = self._analyze_frontend_patterns(repo_data)
        elif "backend" in job_description.title.lower():
            analysis["coding_patterns"] = self._analyze_backend_patterns(repo_data)
        
        # assess code quality
        analysis["code_quality_indicators"] = self._assess_code_quality_deep(repo_data)
        
        # check best practices
        analysis["best_practices"] = self._analyze_best_practices(repo_data)
        
        return analysis
    
    def _analyze_frontend_patterns(self, repo_data: Dict[str, Any]) -> List[str]:
        """Analyze frontend-specific coding patterns."""
        
        patterns = []
        
        # check for modern JavaScript features
        if "JavaScript" in repo_data.get("languages", {}):
            patterns.append("Uses modern JavaScript")
        
        # check for CSS frameworks
        if "CSS" in repo_data.get("languages", {}):
            patterns.append("Implements responsive styling")
        
        # check for HTML structure
        if "HTML" in repo_data.get("languages", {}):
            patterns.append("Creates semantic web interfaces")
        
        # check for TypeScript
        if "TypeScript" in repo_data.get("languages", {}):
            patterns.append("Uses TypeScript for type safety")
        
        return patterns
    
    def _analyze_backend_patterns(self, repo_data: Dict[str, Any]) -> List[str]:
        """Analyze backend-specific coding patterns."""
        
        patterns = []
        
        # check for Python backend
        if "Python" in repo_data.get("languages", {}):
            patterns.append("Uses Python backend development")
        
        # check for Node.js
        if "JavaScript" in repo_data.get("languages", {}):
            patterns.append("Uses Node.js backend")
        
        # check for Java
        if "Java" in repo_data.get("languages", {}):
            patterns.append("Uses Java backend development")
        
        return patterns
    
    def _assess_code_quality_deep(self, repo_data: Dict[str, Any]) -> List[str]:
        """Assess code quality indicators."""
        
        indicators = []
        
        # check for documentation
        if repo_data.get("description"):
            indicators.append("Has project description")
        
        # check for README
        if repo_data.get("has_readme"):
            indicators.append("Has README documentation")
        
        # check for stars (community interest)
        if repo_data.get("stars", 0) > 0:
            indicators.append("Has community interest")
        
        # check for recent activity
        if repo_data.get("last_updated"):
            indicators.append("Recently updated")
        
        return indicators
    
    def _analyze_best_practices(self, repo_data: Dict[str, Any]) -> List[str]:
        """Analyze if best practices are followed."""
        
        practices = []
        
        # check for proper naming
        if repo_data.get("name") and not repo_data["name"].startswith("test"):
            practices.append("Follows naming conventions")
        
        # check for description
        if repo_data.get("description"):
            practices.append("Has clear project description")
        
        return practices
    
    def _generate_analysis_summary(self, analysis_results: Dict[str, Any], job_description) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        
        total_repos = len(analysis_results)
        successful_analyses = sum(1 for result in analysis_results.values() if "error" not in result)
        
        # collect all detected languages and frameworks
        all_languages = set()
        all_frameworks = set()
        
        for result in analysis_results.values():
            if "code_analysis" in result:
                all_languages.update(result["code_analysis"].get("languages_detected", []))
                all_frameworks.update(result["code_analysis"].get("frameworks_detected", []))
        
        return {
            "total_repositories": total_repos,
            "successful_analyses": successful_analyses,
            "languages_found": list(all_languages),
            "frameworks_found": list(all_frameworks),
            "job_relevance": self._assess_job_relevance(all_languages, all_frameworks, job_description)
        }
    
    def _assess_job_relevance(self, languages: set, frameworks: set, job_description) -> str:
        """Assess how relevant the found technologies are to the job."""
        
        job_skills = set(job_description.required_skills + job_description.preferred_skills)
        job_technologies = set(job_description.technologies + job_description.frameworks)
        
        # check for skill matches
        skill_matches = len(languages.intersection(job_technologies))
        framework_matches = len(frameworks.intersection(job_technologies))
        
        total_matches = skill_matches + framework_matches
        
        if total_matches >= 3:
            return "High relevance - Strong technology alignment"
        elif total_matches >= 1:
            return "Moderate relevance - Some technology overlap"
        else:
            return "Low relevance - Limited technology alignment"
    
    def _extract_username_from_url(self, github_url: str) -> Optional[str]:
        """Extract username from GitHub URL."""
        
        # handle different GitHub URL formats
        patterns = [
            r"github\.com/([^/]+)",
            r"github\.com/([^/]+)/?$",
            r"@([^/]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, github_url)
            if match:
                return match.group(1)
        
        return None
    
    def _convert_to_github_profile_data(self, profile_data: Dict[str, Any], github_url: str) -> GitHubProfileData:
        """Convert scanner result to GitHubProfileData schema."""
        
        # extract username from URL for profile_url
        username = self._extract_username_from_url(github_url) or profile_data.get("username", "unknown")
        profile_url = f"https://github.com/{username}"
        
        # convert repositories
        repositories = []
        for repo_dict in profile_data.get("repositories", []):
            # convert languages from dict to list
            languages_dict = repo_dict.get("languages", {})
            languages_list = list(languages_dict.keys()) if isinstance(languages_dict, dict) else []
            
            repo_data = GitHubRepositoryData(
                name=repo_dict.get("name", ""),
                description=repo_dict.get("description", ""),
                url=repo_dict.get("url", ""),
                languages=languages_list,
                stars=repo_dict.get("stars", 0),
                forks=repo_dict.get("forks", 0),
                last_updated=repo_dict.get("last_updated", ""),
                relevance_score=repo_dict.get("relevance_score", 0.0)
            )
            repositories.append(repo_data)
        
        # convert contributions
        contributions_dict = profile_data.get("contributions", {})
        contributions = GitHubContributionData(
            total_contributions=contributions_dict.get("total_contributions", 0),
            total_commits=contributions_dict.get("total_commits", 0),
            total_prs=contributions_dict.get("total_prs", 0),
            total_reviews=contributions_dict.get("total_reviews", 0),
            active_days=contributions_dict.get("active_days", 0),
            contribution_calendar=contributions_dict.get("contribution_calendar", [])
        )
        
        return GitHubProfileData(
            username=username,
            profile_url=profile_url,
            is_valid_url=True,
            name=profile_data.get("name"),
            bio=profile_data.get("bio"),
            location=profile_data.get("location"),
            company=profile_data.get("company"),
            email=profile_data.get("email"),
            website=profile_data.get("website"),
            public_repos=len(repositories),  # use actual repository count
            followers=0,  # not provided by current scanner
            following=0,  # not provided by current scanner
            account_created=profile_data.get("created_at"),
            last_updated=profile_data.get("scan_timestamp"),  # use scan timestamp
            contributions=contributions,
            repositories=repositories,
            profile_summary=profile_data.get("summary", ""),
            scan_errors=profile_data.get("scan_errors", [])
        )
    
    def _create_empty_profile_data(self, github_url: str) -> GitHubProfileData:
        """Create empty profile data when analysis fails."""
        
        username = self._extract_username_from_url(github_url) or "unknown"
        profile_url = f"https://github.com/{username}"
        
        return GitHubProfileData(
            username=username,
            profile_url=profile_url,
            is_valid_url=False,
            name=None,
            bio=None,
            location=None,
            company=None,
            email=None,
            website=None,
            public_repos=0,
            followers=0,
            following=0,
            account_created=None,
            last_updated=None,
            contributions=GitHubContributionData(
                total_contributions=0,
                total_commits=0,
                total_prs=0,
                total_reviews=0,
                active_days=0,
                contribution_calendar=[]
            ),
            repositories=[],
            profile_summary="Profile analysis failed",
            scan_errors=["Failed to analyze GitHub profile"]
        )
