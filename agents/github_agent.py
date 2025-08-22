"""GitHub Agent for scanning GitHub profiles and analyzing user activity."""

import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urljoin

from pydantic import BaseModel, Field

from portia import Portia
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput


class GitHubProfileData(BaseModel):
    """Structured GitHub profile data."""
    
    username: str = Field(description="GitHub username")
    profile_url: str = Field(description="Full GitHub profile URL")
    is_valid_url: bool = Field(description="Whether the URL is valid")
    
    # Profile information
    name: Optional[str] = Field(description="Full name from profile", default=None)
    bio: Optional[str] = Field(description="Profile bio", default=None)
    location: Optional[str] = Field(description="Location", default=None)
    company: Optional[str] = Field(description="Company", default=None)
    website: Optional[str] = Field(description="Website", default=None)
    twitter: Optional[str] = Field(description="Twitter handle", default=None)
    
    # Activity metrics
    public_repos: int = Field(description="Number of public repositories", default=0)
    public_gists: int = Field(description="Number of public gists", default=0)
    followers: int = Field(description="Number of followers", default=0)
    following: int = Field(description="Number of following", default=0)
    account_created: Optional[str] = Field(description="Account creation date", default=None)
    last_active: Optional[str] = Field(description="Last activity date", default=None)
    
    # Repository analysis
    repositories: List[Dict[str, Any]] = Field(description="List of repositories", default_factory=list)
    languages_used: Dict[str, int] = Field(description="Languages and their usage count", default_factory=dict)
    top_languages: List[str] = Field(description="Top programming languages used", default_factory=list)
    
    # Activity analysis
    commit_frequency: str = Field(description="Commit frequency analysis", default="Unknown")
    project_consistency: str = Field(description="Project consistency analysis", default="Unknown")
    collaboration_level: str = Field(description="Collaboration level analysis", default="Unknown")
    
    # Assessment
    overall_activity_score: float = Field(description="Overall activity score (0-10)", default=0.0)
    technical_depth: str = Field(description="Technical depth assessment", default="Unknown")
    code_quality_indicators: List[str] = Field(description="Code quality indicators", default_factory=list)
    
    # Warnings and errors
    scan_warnings: List[str] = Field(description="Warnings during scanning", default_factory=list)
    scan_errors: List[str] = Field(description="Errors during scanning", default_factory=list)


class GitHubAgent:
    """GitHub agent that scans GitHub profiles and analyzes user activity."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
    
    def create_github_analysis_plan(self) -> PlanBuilderV2:
        """Create a plan for comprehensive GitHub profile analysis."""
        
        def validate_github_url(github_url: str) -> Dict[str, Any]:
            """Validate and clean up GitHub URL."""
            if not github_url:
                return {
                    "is_valid": False,
                    "cleaned_url": "",
                    "username": "",
                    "error": "No GitHub URL provided"
                }
            
            # Clean up the URL
            url = github_url.strip()
            
            # Handle different URL formats
            if url.startswith('github.com/'):
                url = f"https://{url}"
            elif not url.startswith('http'):
                url = f"https://github.com/{url}"
            
            # Extract username from URL
            try:
                parsed = urlparse(url)
                if parsed.netloc == 'github.com':
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts:
                        username = path_parts[0]
                        return {
                            "is_valid": True,
                            "cleaned_url": f"https://github.com/{username}",
                            "username": username,
                            "error": None
                        }
            except Exception as e:
                pass
            
            return {
                "is_valid": False,
                "cleaned_url": url,
                "username": "",
                "error": "Invalid GitHub URL format"
            }
        
        def analyze_github_activity(github_data: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze GitHub activity patterns."""
            # This will be enhanced when tools are added
            # For now, return basic analysis based on available data
            
            analysis = {
                "commit_frequency": "Unknown",
                "project_consistency": "Unknown", 
                "collaboration_level": "Unknown",
                "overall_activity_score": 0.0,
                "technical_depth": "Unknown",
                "code_quality_indicators": []
            }
            
            if github_data.get("public_repos", 0) > 0:
                analysis["project_consistency"] = "Has public repositories"
                analysis["overall_activity_score"] += 2.0
            
            if github_data.get("followers", 0) > 0:
                analysis["collaboration_level"] = "Has followers"
                analysis["overall_activity_score"] += 1.0
            
            if github_data.get("languages_used"):
                analysis["technical_depth"] = f"Uses {len(github_data['languages_used'])} programming languages"
                analysis["overall_activity_score"] += 1.0
            
            return analysis
        
        # Create the plan
        plan = PlanBuilderV2("Analyze GitHub profile and provide comprehensive insights")
        
        # Define inputs
        plan.input(
            name="github_url",
            description="GitHub profile URL or username to analyze"
        )
        
        # Step 1: Validate and clean GitHub URL
        plan.function_step(
            function=validate_github_url,
            step_name="validate_github_url",
            args={
                "github_url": Input("github_url")
            }
        )
        
        # Step 2: Scan GitHub profile (placeholder for tool)
        plan.llm_step(
            task="Scan the GitHub profile and extract comprehensive information about the user's activity, repositories, languages used, and overall GitHub presence. Return detailed analysis in JSON format.",
            inputs=[
                StepOutput("validate_github_url")
            ],
            step_name="scan_github_profile"
        )
        
        # Step 3: Analyze activity patterns
        plan.function_step(
            function=analyze_github_activity,
            step_name="analyze_activity",
            args={
                "github_data": StepOutput("scan_github_profile")
            }
        )
        
        # Step 4: Generate insights using LLM
        plan.llm_step(
            task="Based on the GitHub profile analysis, provide insights about the candidate's technical skills, activity level, project consistency, and overall GitHub presence. Include recommendations for improvement.",
            inputs=[
                StepOutput("scan_github_profile"),
                StepOutput("analyze_activity")
            ],
            step_name="generate_github_insights"
        )
        
        # Set final output
        plan.final_output(
            output_schema=GitHubProfileData,
            summarize=True
        )
        
        return plan
    
    def analyze_github_profile(self, github_url: str) -> GitHubProfileData:
        """Analyze a GitHub profile using the planning system."""
        
        if not github_url:
            return GitHubProfileData(
                username="",
                profile_url="",
                is_valid_url=False,
                scan_errors=["No GitHub URL provided"]
            )
        
        # Validate and clean the URL
        validation_result = self._validate_github_url(github_url)
        
        if not validation_result["is_valid"]:
            return GitHubProfileData(
                username=validation_result["username"],
                profile_url=validation_result["cleaned_url"],
                is_valid_url=False,
                scan_errors=[validation_result["error"]]
            )
        
        # Get the LLM from Portia's config
        try:
            llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
        except:
            try:
                llm = self.portia.config.get_generative_model("openai/gpt-4o")
            except:
                llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
        
        # For now, create a placeholder analysis
        # This will be enhanced when GitHub scanning tools are added
        profile_data = self._create_placeholder_analysis(validation_result, llm)
        
        return profile_data
    
    def _validate_github_url(self, github_url: str) -> Dict[str, Any]:
        """Validate and clean up GitHub URL."""
        if not github_url:
            return {
                "is_valid": False,
                "cleaned_url": "",
                "username": "",
                "error": "No GitHub URL provided"
            }
        
        # Clean up the URL
        url = github_url.strip()
        
        # Handle different URL formats
        if url.startswith('github.com/'):
            url = f"https://{url}"
        elif not url.startswith('http'):
            url = f"https://github.com/{url}"
        
        # Extract username from URL
        try:
            parsed = urlparse(url)
            if parsed.netloc == 'github.com':
                path_parts = parsed.path.strip('/').split('/')
                if path_parts:
                    username = path_parts[0]
                    return {
                        "is_valid": True,
                        "cleaned_url": f"https://github.com/{username}",
                        "username": username,
                        "error": None
                    }
        except Exception as e:
            pass
        
        return {
            "is_valid": False,
            "cleaned_url": url,
            "username": "",
            "error": "Invalid GitHub URL format"
        }
    
    def _create_placeholder_analysis(self, validation_result: Dict[str, Any], llm) -> GitHubProfileData:
        """Create analysis using GitHub scanner tool if available, otherwise use placeholder."""
        
        # Try to use GitHub scanner tool
        try:
            from tools.github_scanner import GitHubScanner
            scanner = GitHubScanner()
            scan_result = scanner.scan_profile(validation_result["username"])
            
            if scan_result["scan_success"]:
                return self._process_github_scan_result(scan_result, validation_result)
            else:
                # Fall back to LLM analysis if scanner fails
                return self._create_llm_analysis(validation_result, llm)
                
        except ImportError:
            # Fall back to LLM analysis if tool not available
            return self._create_llm_analysis(validation_result, llm)
    
    def _process_github_scan_result(self, scan_result: Dict[str, Any], validation_result: Dict[str, Any]) -> GitHubProfileData:
        """Process the results from GitHub scanner tool."""
        profile = scan_result.get("profile", {})
        repos = scan_result.get("repositories", [])
        languages = scan_result.get("languages", {})
        activity_metrics = scan_result.get("activity_metrics", {})
        
        # Calculate top languages
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        top_languages_list = [lang for lang, count in top_languages]
        
        # Calculate activity score
        activity_score = 0.0
        if activity_metrics.get("total_repos", 0) > 0:
            activity_score += 2.0
        if activity_metrics.get("recent_activity", False):
            activity_score += 2.0
        if activity_metrics.get("total_stars", 0) > 0:
            activity_score += 1.0
        if activity_metrics.get("followers", 0) > 0:
            activity_score += 1.0
        if len(languages) > 0:
            activity_score += 1.0
        
        return GitHubProfileData(
            username=validation_result["username"],
            profile_url=validation_result["cleaned_url"],
            is_valid_url=True,
            name=profile.get("name"),
            bio=profile.get("bio"),
            location=profile.get("location"),
            company=profile.get("company"),
            website=profile.get("blog"),
            twitter=profile.get("twitter_username"),
            public_repos=profile.get("public_repos", 0),
            public_gists=profile.get("public_gists", 0),
            followers=profile.get("followers", 0),
            following=profile.get("following", 0),
            account_created=profile.get("created_at"),
            last_active=profile.get("updated_at"),
            repositories=repos,
            languages_used=languages,
            top_languages=top_languages_list,
            commit_frequency="High" if activity_metrics.get("recent_activity") else "Low",
            project_consistency="Good" if activity_metrics.get("total_repos", 0) > 5 else "Limited",
            collaboration_level="Active" if activity_metrics.get("followers", 0) > 10 else "Limited",
            overall_activity_score=min(activity_score, 10.0),
            technical_depth=f"Uses {len(languages)} programming languages",
            code_quality_indicators=["Has public repositories", "Active development"] if repos else [],
            scan_warnings=[],
            scan_errors=[]
        )
    
    def _create_llm_analysis(self, validation_result: Dict[str, Any], llm) -> GitHubProfileData:
        """Create LLM-based analysis as fallback."""
        
        # Create a prompt for the LLM to analyze the GitHub profile
        prompt = f"""
You are a GitHub profile analyzer. Analyze the GitHub profile at {validation_result['cleaned_url']} and provide insights.

Since we don't have direct API access yet, provide a comprehensive analysis based on what you can infer about GitHub profiles in general and provide recommendations for what to look for when scanning this profile.

Please return your analysis in JSON format with the following structure:
{{
    "name": "Full name if available",
    "bio": "Profile bio if available",
    "location": "Location if available",
    "company": "Company if available",
    "website": "Website if available",
    "twitter": "Twitter handle if available",
    "public_repos": 0,
    "public_gists": 0,
    "followers": 0,
    "following": 0,
    "account_created": "Account creation date if available",
    "last_active": "Last activity date if available",
    "repositories": [],
    "languages_used": {{}},
    "top_languages": [],
    "commit_frequency": "Analysis of commit frequency",
    "project_consistency": "Analysis of project consistency",
    "collaboration_level": "Analysis of collaboration level",
    "overall_activity_score": 0.0,
    "technical_depth": "Assessment of technical depth",
    "code_quality_indicators": [],
    "scan_warnings": ["Placeholder analysis - GitHub scanning tools not yet implemented"],
    "scan_errors": []
}}

Focus on providing useful insights about what to look for when scanning GitHub profiles for recruitment purposes.
"""
        
        try:
            from portia.model import Message
            message = Message(role="user", content=prompt)
            response = llm.get_response([message])
            
            # Parse the JSON response
            response_text = response.content
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                analysis_data = json.loads(json_str)
            else:
                analysis_data = {}
                
        except Exception as e:
            analysis_data = {
                "scan_errors": [f"Failed to analyze GitHub profile: {str(e)}"]
            }
        
        # Create the GitHubProfileData object
        return GitHubProfileData(
            username=validation_result["username"],
            profile_url=validation_result["cleaned_url"],
            is_valid_url=True,
            name=analysis_data.get("name"),
            bio=analysis_data.get("bio"),
            location=analysis_data.get("location"),
            company=analysis_data.get("company"),
            website=analysis_data.get("website"),
            twitter=analysis_data.get("twitter"),
            public_repos=analysis_data.get("public_repos", 0),
            public_gists=analysis_data.get("public_gists", 0),
            followers=analysis_data.get("followers", 0),
            following=analysis_data.get("following", 0),
            account_created=analysis_data.get("account_created"),
            last_active=analysis_data.get("last_active"),
            repositories=analysis_data.get("repositories", []),
            languages_used=analysis_data.get("languages_used", {}),
            top_languages=analysis_data.get("top_languages", []),
            commit_frequency=analysis_data.get("commit_frequency", "Unknown"),
            project_consistency=analysis_data.get("project_consistency", "Unknown"),
            collaboration_level=analysis_data.get("collaboration_level", "Unknown"),
            overall_activity_score=analysis_data.get("overall_activity_score", 0.0),
            technical_depth=analysis_data.get("technical_depth", "Unknown"),
            code_quality_indicators=analysis_data.get("code_quality_indicators", []),
            scan_warnings=analysis_data.get("scan_warnings", []),
            scan_errors=analysis_data.get("scan_errors", [])
        )
