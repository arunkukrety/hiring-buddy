"""GitHub Scanner Tool for analyzing GitHub profiles and repositories."""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from pydantic import BaseModel, Field


class GitHubContribution(BaseModel):
    """GitHub contribution data."""
    total_commits: int = Field(description="Total commit contributions")
    total_prs: int = Field(description="Total pull request contributions")
    total_reviews: int = Field(description="Total pull request review contributions")
    total_contributions: int = Field(description="Total contributions in calendar")
    contribution_days: List[Dict[str, Any]] = Field(description="Non-zero contribution days", default_factory=list)


class GitHubRepository(BaseModel):
    """GitHub repository data."""
    name: str = Field(description="Repository name")
    languages: Dict[str, int] = Field(description="Languages used in repository", default_factory=dict)
    commit_count: int = Field(description="Number of commits", default=0)
    pr_count: int = Field(description="Number of pull requests", default=0)
    relevance_score: float = Field(description="Relevance score (0-1)", default=0.0)
    description: str = Field(description="Repository description or analysis", default="")


class GitHubScanner:
    """Advanced GitHub profile and repository scanner using GraphQL API."""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.api_url = "https://api.github.com/graphql"
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def scan_profile_comprehensive(self, username: str) -> Dict[str, Any]:
        """Comprehensive GitHub profile scan using GraphQL API."""
        print(f"🔍 Scanning GitHub profile for: {username}")
        
        # GraphQL query for comprehensive profile data
        query = """
        query($username: String!) {
          user(login: $username) {
            name
            login
            bio
            company
            location
            email
            websiteUrl
            createdAt
            repositories(first: 50, privacy: PUBLIC, ownerAffiliations: OWNER, orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes {
                name
                description
                url
                stargazerCount
                forkCount
                isPrivate
                isFork
                primaryLanguage {
                  name
                  color
                }
                languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                  edges {
                    size
                    node {
                      name
                      color
                    }
                  }
                }
                defaultBranchRef {
                  target {
                    ... on Commit {
                      history(first: 1) {
                        totalCount
                      }
                    }
                  }
                }
                pullRequests(first: 10, states: MERGED) {
                  totalCount
                }
                pushedAt
                createdAt
              }
            }
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
            }
          }
        }
        """
        
        variables = {"username": username}
        
        try:
            print("⏳ Sending GraphQL request to GitHub API...")
            response = requests.post(
                self.api_url, 
                json={"query": query, "variables": variables}, 
                headers=self.headers
            )
            
            if response.status_code != 200:
                raise Exception(f"❌ GraphQL query failed with status code {response.status_code}: {response.text}")
            
            print("✅ Response received from GitHub API")
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                print("⚠️ GraphQL Errors:", data["errors"])
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            user = data.get("data", {}).get("user")
            if not user:
                raise Exception("⚠️ No user data found. Maybe wrong username or invalid token?")
            
            # Process repositories
            repositories = []
            for repo in user.get("repositories", {}).get("nodes", []):
                if repo and not repo.get("isPrivate", True):
                    repo_data = self._process_repository_data(repo)
                    repositories.append(repo_data)
            
            # Process contributions
            contributions = self._process_contributions_data(user.get("contributionsCollection", {}))
            
            # Generate summary
            summary = self._generate_profile_summary(user, repositories, contributions)
            
            # Create result
            result = {
                "username": user.get("login", username),
                "name": user.get("name", ""),
                "bio": user.get("bio", ""),
                "company": user.get("company", ""),
                "location": user.get("location", ""),
                "email": user.get("email", ""),
                "website": user.get("websiteUrl", ""),
                "created_at": user.get("createdAt", ""),
                "repositories": [repo.model_dump() for repo in repositories],
                "contributions": contributions.model_dump(),
                "summary": summary,
                "scan_timestamp": datetime.now().isoformat()
            }
            
            # Save results
            self.save_scan_results(result, username)
            
            return result
            
        except Exception as e:
            print(f"❌ GitHub scan failed: {str(e)}")
            raise
    
    def _process_repository_data(self, repo: Dict[str, Any]) -> GitHubRepository:
        """Process repository data from GraphQL response."""
        # Extract languages
        languages = {}
        for lang_edge in repo.get("languages", {}).get("edges", []):
            lang_name = lang_edge["node"]["name"]
            lang_size = lang_edge["size"]
            languages[lang_name] = lang_size
        
        # Get commit count
        commit_count = 0
        if repo.get("defaultBranchRef", {}).get("target", {}).get("history", {}):
            commit_count = repo["defaultBranchRef"]["target"]["history"]["totalCount"]
        
        # Get PR count
        pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
        
        # Calculate relevance score
        relevance_score = self._calculate_repository_relevance(repo, languages, commit_count, pr_count)
        
        # Generate description
        description = self._generate_repository_description(repo, languages)
        
        return GitHubRepository(
            name=repo.get("name", ""),
            languages=languages,
            commit_count=commit_count,
            pr_count=pr_count,
            relevance_score=relevance_score,
            description=description
        )
    
    def _process_contributions_data(self, contributions_data: Dict[str, Any]) -> GitHubContribution:
        """Process contributions data from GraphQL response."""
        calendar = contributions_data.get("contributionCalendar", {})
        
        # Filter out zero contribution days
        filtered_days = []
        for week in calendar.get("weeks", []):
            for day in week.get("contributionDays", []):
                if day.get("contributionCount", 0) > 0:
                    filtered_days.append(day)
        
        return GitHubContribution(
            total_commits=contributions_data.get("totalCommitContributions", 0),
            total_prs=contributions_data.get("totalPullRequestContributions", 0),
            total_reviews=contributions_data.get("totalPullRequestReviewContributions", 0),
            total_contributions=calendar.get("totalContributions", 0),
            contribution_days=filtered_days
        )
    
    def _calculate_repository_relevance(self, repo: Dict[str, Any], languages: Dict[str, int], commit_count: int, pr_count: int) -> float:
        """Calculate repository relevance score (0-1)."""
        score = 0.0
        
        # Base score from activity
        if commit_count > 0:
            score += min(commit_count / 100.0, 0.3)  # Max 0.3 for commits
        
        if pr_count > 0:
            score += min(pr_count / 50.0, 0.2)  # Max 0.2 for PRs
        
        # Score from stars
        stars = repo.get("stargazerCount", 0)
        if stars > 0:
            score += min(stars / 100.0, 0.2)  # Max 0.2 for stars
        
        # Score from forks
        forks = repo.get("forkCount", 0)
        if forks > 0:
            score += min(forks / 50.0, 0.1)  # Max 0.1 for forks
        
        # Score from recency (recently pushed)
        if repo.get("pushedAt"):
            pushed_date = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00"))
            days_since_push = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            if days_since_push < 30:
                score += 0.2  # Bonus for recent activity
        
        return min(score, 1.0)
    
    def _generate_repository_description(self, repo: Dict[str, Any], languages: Dict[str, int]) -> str:
        """Generate description for repository."""
        description = repo.get("description", "")
        
        if not description:
            # Generate description based on languages and activity
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            lang_names = [lang[0] for lang in top_languages]
            
            if lang_names:
                description = f"Repository using {', '.join(lang_names)}"
            else:
                description = "Repository with no detected languages"
        
        return description
    
    def _generate_profile_summary(self, user: Dict[str, Any], repositories: List[GitHubRepository], contributions: GitHubContribution) -> str:
        """Generate comprehensive profile summary."""
        username = user.get("login", "Unknown")
        name = user.get("name", username)
        
        # Repository analysis
        total_repos = len(repositories)
        active_repos = len([r for r in repositories if r.commit_count > 0])
        top_languages = {}
        
        for repo in repositories:
            for lang, size in repo.languages.items():
                top_languages[lang] = top_languages.get(lang, 0) + size
        
        sorted_languages = sorted(top_languages.items(), key=lambda x: x[1], reverse=True)[:5]
        lang_names = [lang[0] for lang in sorted_languages]
        
        # Contribution analysis
        total_contributions = contributions.total_contributions
        active_days = len(contributions.contribution_days)
        
        # Generate summary
        summary_parts = [
            f"GitHub profile for {name} ({username})",
            f"Total repositories: {total_repos} (with {active_repos} showing activity)",
            f"Top languages: {', '.join(lang_names) if lang_names else 'None detected'}",
            f"Total contributions: {total_contributions}",
            f"Active contribution days: {active_days}",
            f"Commits: {contributions.total_commits}, PRs: {contributions.total_prs}, Reviews: {contributions.total_reviews}"
        ]
        
        if user.get("bio"):
            summary_parts.append(f"Bio: {user['bio']}")
        
        if user.get("company"):
            summary_parts.append(f"Company: {user['company']}")
        
        return " | ".join(summary_parts)
    
    def save_scan_results(self, results: Dict[str, Any], username: str) -> str:
        """Save scan results to JSON file."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"github_scan_{username}_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 GitHub scan results saved to: {filepath}")
        return str(filepath)

