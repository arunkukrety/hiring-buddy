"""Skill matching tool for analyzing candidate skills against job requirements."""

from typing import Any, Optional, List, Dict

from utils.schemas import JobDescription, CandidateFacts
from agents.github_agent import GitHubProfileData


class SkillMatcher:
    """Tool for intelligent skill matching using multiple evidence sources."""
    
    def __init__(self):
        pass
    
    def intelligent_skill_matching_with_info(self, candidate_info: dict, job_description: JobDescription, github_analysis: Optional[GitHubProfileData]) -> List[Dict[str, Any]]:
        """Intelligent skill matching using GitHub evidence and repository analysis with candidate info dict."""
        
        skill_matches = []
        
        # get all candidate skills from resume info
        resume_skills = []
        if candidate_info.get('skills'):
            skills = candidate_info['skills']
            resume_skills.extend(skills.get('primary', []))
            resume_skills.extend(skills.get('secondary', []))
            resume_skills.extend(skills.get('tools', []))
        
        # extract skills from GitHub repositories
        github_skills = self._extract_skills_from_github(github_analysis)
        
        # combine all evidence
        all_evidence = resume_skills + github_skills
        
        # match required skills with intelligent scoring
        for skill in job_description.required_skills:
            match_score = self._calculate_skill_match_score(skill, all_evidence, github_analysis, job_description)
            skill_matches.append({
                "skill": skill,
                "required": True,
                "candidate_has": match_score > 0.3,  # threshold for "has skill"
                "match_score": match_score,
                "evidence": self._get_skill_evidence(skill, all_evidence, github_analysis)
            })
        
        # match preferred skills
        for skill in job_description.preferred_skills:
            match_score = self._calculate_skill_match_score(skill, all_evidence, github_analysis, job_description)
            skill_matches.append({
                "skill": skill,
                "required": False,
                "candidate_has": match_score > 0.3,
                "match_score": match_score,
                "evidence": self._get_skill_evidence(skill, all_evidence, github_analysis)
            })
        
        return skill_matches
    
    def intelligent_skill_matching(self, candidate_facts: CandidateFacts, job_description: JobDescription, github_analysis: Optional[GitHubProfileData]) -> List[Dict[str, Any]]:
        """Intelligent skill matching using GitHub evidence and repository analysis."""
        
        skill_matches = []
        
        # get all candidate skills from resume
        resume_skills = (
            candidate_facts.skills.primary + 
            candidate_facts.skills.secondary + 
            candidate_facts.skills.tools
        )
        
        # extract skills from GitHub repositories
        github_skills = self._extract_skills_from_github(github_analysis)
        
        # combine all evidence
        all_evidence = resume_skills + github_skills
        
        # match required skills with intelligent scoring
        for skill in job_description.required_skills:
            match_score = self._calculate_skill_match_score(skill, all_evidence, github_analysis, job_description)
            skill_matches.append({
                "skill": skill,
                "required": True,
                "candidate_has": match_score > 0.3,  # threshold for "has skill"
                "match_score": match_score,
                "evidence": self._get_skill_evidence(skill, all_evidence, github_analysis)
            })
        
        # match preferred skills
        for skill in job_description.preferred_skills:
            match_score = self._calculate_skill_match_score(skill, all_evidence, github_analysis, job_description)
            skill_matches.append({
                "skill": skill,
                "required": False,
                "candidate_has": match_score > 0.3,
                "match_score": match_score,
                "evidence": self._get_skill_evidence(skill, all_evidence, github_analysis)
            })
        
        return skill_matches
    
    def match_skills_against_job(self, candidate_facts: CandidateFacts, job_description: JobDescription) -> List[Dict[str, Any]]:
        """Match candidate skills against job requirements."""
        
        skill_matches = []
        all_candidate_skills = (
            candidate_facts.skills.primary + 
            candidate_facts.skills.secondary + 
            candidate_facts.skills.tools
        )
        
        # match required skills
        for skill in job_description.required_skills:
            candidate_has = any(
                skill.lower() in candidate_skill.lower() 
                for candidate_skill in all_candidate_skills
            )
            skill_matches.append({
                "skill": skill,
                "required": True,
                "candidate_has": candidate_has,
                "match_score": 1.0 if candidate_has else 0.0
            })
        
        # match preferred skills
        for skill in job_description.preferred_skills:
            candidate_has = any(
                skill.lower() in candidate_skill.lower() 
                for candidate_skill in all_candidate_skills
            )
            skill_matches.append({
                "skill": skill,
                "required": False,
                "candidate_has": candidate_has,
                "match_score": 0.7 if candidate_has else 0.0
            })
        
        return skill_matches
    
    def _extract_skills_from_github(self, github_analysis: Optional[GitHubProfileData]) -> List[str]:
        """Extract skills from GitHub repositories and profile."""
        
        if not github_analysis or not github_analysis.repositories:
            return []
        
        skills = []
        
        # extract from languages
        for repo in github_analysis.repositories:
            skills.extend(repo.languages)
        
        # extract from repository names and descriptions
        for repo in github_analysis.repositories:
            if repo.description:
                # look for common skill keywords in descriptions
                description_lower = repo.description.lower()
                skill_keywords = [
                    "react", "angular", "vue", "node", "express", "python", "java", "javascript",
                    "typescript", "html", "css", "bootstrap", "tailwind", "material-ui", "redux",
                    "git", "docker", "aws", "azure", "sql", "mongodb", "postgresql"
                ]
                for keyword in skill_keywords:
                    if keyword in description_lower:
                        skills.append(keyword.title())
        
        # extract from repository names
        for repo in github_analysis.repositories:
            name_lower = repo.name.lower()
            if "react" in name_lower:
                skills.append("React")
            if "vue" in name_lower:
                skills.append("Vue")
            if "angular" in name_lower:
                skills.append("Angular")
            if "node" in name_lower:
                skills.append("Node.js")
            if "express" in name_lower:
                skills.append("Express")
        
        return list(set(skills))  # remove duplicates
    
    def _calculate_skill_match_score(self, skill: str, all_evidence: List[str], github_analysis: Optional[GitHubProfileData], job_description: JobDescription) -> float:
        """Calculate intelligent skill match score based on multiple evidence sources."""
        
        score = 0.0
        skill_lower = skill.lower()
        
        # 1. Direct skill match from resume or GitHub (40% weight)
        direct_match = any(skill_lower in evidence.lower() for evidence in all_evidence)
        if direct_match:
            score += 0.4
        
        # 2. Language-based evidence (30% weight)
        if github_analysis and github_analysis.repositories:
            language_evidence = self._check_language_evidence(skill_lower, github_analysis.repositories)
            score += 0.3 * language_evidence
        
        # 3. Repository-based evidence (20% weight)
        if github_analysis and github_analysis.repositories:
            repo_evidence = self._check_repository_evidence(skill_lower, github_analysis.repositories)
            score += 0.2 * repo_evidence
        
        # 4. Activity-based evidence (10% weight)
        if github_analysis:
            activity_score = self._calculate_activity_score(github_analysis)
            score += 0.1 * activity_score
        
        return min(score, 1.0)
    
    def _check_language_evidence(self, skill: str, repositories: List) -> float:
        """Check if skill is evidenced by programming languages used."""
        
        # skill to language mapping
        skill_language_map = {
            "javascript": ["javascript", "js"],
            "typescript": ["typescript", "ts"],
            "html": ["html"],
            "css": ["css"],
            "react": ["javascript", "typescript"],  # React uses JS/TS
            "angular": ["typescript", "javascript"],
            "vue": ["javascript", "typescript"],
            "python": ["python"],
            "java": ["java"],
            "node.js": ["javascript", "typescript"],
            "express": ["javascript", "typescript"]
        }
        
        if skill not in skill_language_map:
            return 0.0
        
        target_languages = skill_language_map[skill]
        repo_languages = []
        
        for repo in repositories:
            repo_languages.extend([lang.lower() for lang in repo.languages])
        
        # check if any target language is used
        for target_lang in target_languages:
            if target_lang in repo_languages:
                return 1.0
        
        return 0.0
    
    def _check_repository_evidence(self, skill: str, repositories: List) -> float:
        """Check if skill is evidenced by repository names and descriptions."""
        
        evidence_count = 0
        
        for repo in repositories:
            # check repository name
            if skill in repo.name.lower():
                evidence_count += 1
            
            # check repository description
            if repo.description and skill in repo.description.lower():
                evidence_count += 1
        
        # normalize to 0-1 scale
        return min(evidence_count / 3.0, 1.0)  # max 3 pieces of evidence
    
    def _calculate_activity_score(self, github_analysis: GitHubProfileData) -> float:
        """Calculate activity score based on GitHub contributions."""
        
        if not github_analysis.contributions:
            return 0.0
        
        # normalize based on contribution levels
        total_contributions = github_analysis.contributions.total_contributions
        total_commits = github_analysis.contributions.total_commits
        active_days = github_analysis.contributions.active_days
        
        # scoring logic:
        # - High activity: >500 contributions, >200 commits, >100 active days
        # - Medium activity: >200 contributions, >100 commits, >50 active days
        # - Low activity: >50 contributions, >20 commits, >10 active days
        
        if total_contributions > 500 and total_commits > 200 and active_days > 100:
            return 1.0
        elif total_contributions > 200 and total_commits > 100 and active_days > 50:
            return 0.7
        elif total_contributions > 50 and total_commits > 20 and active_days > 10:
            return 0.4
        else:
            return 0.1
    
    def _get_skill_evidence(self, skill: str, all_evidence: List[str], github_analysis: Optional[GitHubProfileData]) -> List[str]:
        """Get evidence for a specific skill."""
        
        evidence = []
        skill_lower = skill.lower()
        
        # check resume evidence
        for evidence_item in all_evidence:
            if skill_lower in evidence_item.lower():
                evidence.append(f"Resume: {evidence_item}")
        
        # check GitHub evidence
        if github_analysis and github_analysis.repositories:
            for repo in github_analysis.repositories:
                if skill_lower in repo.name.lower():
                    evidence.append(f"Repository: {repo.name}")
                if repo.description and skill_lower in repo.description.lower():
                    evidence.append(f"Repository description: {repo.name}")
                if skill_lower in [lang.lower() for lang in repo.languages]:
                    evidence.append(f"Language used: {repo.name}")
        
        return evidence[:3]  # limit to 3 pieces of evidence
    
    def calculate_skill_match_component(self, skill_matches: List[Dict[str, Any]]) -> float:
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
