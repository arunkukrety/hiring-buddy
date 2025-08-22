"""GitHub Scanner Tool for analyzing GitHub profiles."""

import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class GitHubScanner:
    """Tool for scanning GitHub profiles and extracting data."""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.base_url = "https://api.github.com"
        self.headers = {}
        
        if api_token:
            self.headers["Authorization"] = f"token {api_token}"
    
    def scan_profile(self, username: str) -> Dict[str, Any]:
        """Scan a GitHub profile and return comprehensive data."""
        try:
            # Get user profile
            profile_data = self._get_user_profile(username)
            
            # Get repositories
            repos_data = self._get_user_repositories(username)
            
            # Get languages used
            languages_data = self._analyze_languages(username, repos_data)
            
            # Combine all data
            return {
                "profile": profile_data,
                "repositories": repos_data,
                "languages": languages_data,
                "activity_metrics": self._calculate_activity_metrics(repos_data),
                "scan_success": True
            }
            
        except Exception as e:
            return {
                "scan_success": False,
                "error": str(e),
                "profile": {},
                "repositories": [],
                "languages": {},
                "activity_metrics": {}
            }
    
    def _get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile information."""
        url = f"{self.base_url}/users/{username}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name"),
                "bio": data.get("bio"),
                "location": data.get("location"),
                "company": data.get("company"),
                "blog": data.get("blog"),
                "twitter_username": data.get("twitter_username"),
                "public_repos": data.get("public_repos", 0),
                "public_gists": data.get("public_gists", 0),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at")
            }
        else:
            raise Exception(f"Failed to get profile: {response.status_code}")
    
    def _get_user_repositories(self, username: str) -> list:
        """Get user repositories."""
        url = f"{self.base_url}/users/{username}/repos"
        params = {"sort": "updated", "per_page": 100}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            repos = response.json()
            return [
                {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "forks_count": repo.get("forks_count", 0),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "html_url": repo.get("html_url"),
                    "fork": repo.get("fork", False)
                }
                for repo in repos
            ]
        else:
            return []
    
    def _analyze_languages(self, username: str, repos: list) -> Dict[str, int]:
        """Analyze programming languages used across repositories."""
        languages = {}
        
        for repo in repos:
            if repo.get("language"):
                lang = repo["language"]
                languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def _calculate_activity_metrics(self, repos: list) -> Dict[str, Any]:
        """Calculate activity metrics from repositories."""
        if not repos:
            return {
                "total_repos": 0,
                "original_repos": 0,
                "forked_repos": 0,
                "total_stars": 0,
                "total_forks": 0,
                "avg_stars_per_repo": 0,
                "recent_activity": False
            }
        
        total_repos = len(repos)
        original_repos = len([r for r in repos if not r.get("fork", False)])
        forked_repos = total_repos - original_repos
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        avg_stars = total_stars / total_repos if total_repos > 0 else 0
        
        # Check for recent activity (repos updated in last 6 months)
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_activity = any(
            datetime.fromisoformat(r.get("updated_at", "").replace("Z", "+00:00")) > six_months_ago
            for r in repos
        )
        
        return {
            "total_repos": total_repos,
            "original_repos": original_repos,
            "forked_repos": forked_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "avg_stars_per_repo": avg_stars,
            "recent_activity": recent_activity
        }

