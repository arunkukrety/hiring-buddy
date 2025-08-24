"""Enhanced Skills Extractor Tool for AI-powered skills detection."""

import re
from typing import Dict, List, Any, Set
from pydantic import BaseModel, Field


class SkillsData(BaseModel):
    """Structured skills data with enhanced detection."""
    
    programming_languages: List[str] = Field(description="Programming languages", default_factory=list)
    frameworks: List[str] = Field(description="Frameworks and libraries", default_factory=list)
    databases: List[str] = Field(description="Databases and data storage", default_factory=list)
    cloud_platforms: List[str] = Field(description="Cloud platforms and services", default_factory=list)
    tools: List[str] = Field(description="Development tools and utilities", default_factory=list)
    methodologies: List[str] = Field(description="Development methodologies and practices", default_factory=list)
    soft_skills: List[str] = Field(description="Soft skills and competencies", default_factory=list)
    
    # normalized versions for better matching
    all_skills: List[str] = Field(description="All skills in normalized format", default_factory=list)
    skill_count: int = Field(description="Total number of unique skills", default=0)


class SkillsExtractor:
    """Enhanced tool for extracting and categorizing skills from resume and GitHub data."""
    
    def __init__(self):
        # comprehensive skill mappings for normalization
        self.skill_mappings = {
            # programming languages
            "javascript": ["js", "javascript", "es6", "es2015", "node.js", "nodejs"],
            "python": ["python", "py", "python3", "python 3"],
            "java": ["java", "j2ee", "j2se", "spring"],
            "c++": ["c++", "cpp", "c plus plus"],
            "c#": ["c#", "csharp", "dotnet", ".net"],
            "php": ["php", "php7", "php8"],
            "ruby": ["ruby", "rails", "ruby on rails"],
            "go": ["go", "golang"],
            "rust": ["rust"],
            "swift": ["swift", "ios"],
            "kotlin": ["kotlin", "android"],
            "typescript": ["typescript", "ts"],
            "scala": ["scala"],
            "r": ["r", "r language"],
            "matlab": ["matlab"],
            "sql": ["sql", "mysql", "postgresql", "sqlite"],
            
            # frameworks and libraries
            "react": ["react", "react.js", "reactjs", "react native"],
            "angular": ["angular", "angularjs", "angular 2"],
            "vue": ["vue", "vue.js", "vuejs"],
            "express": ["express", "express.js", "expressjs"],
            "django": ["django", "django framework"],
            "flask": ["flask", "flask framework"],
            "spring": ["spring", "spring boot", "spring framework"],
            "laravel": ["laravel", "laravel framework"],
            "asp.net": ["asp.net", "aspnet", "asp net"],
            "jquery": ["jquery", "jq"],
            "bootstrap": ["bootstrap", "bootstrap 4", "bootstrap 5"],
            "tailwind": ["tailwind", "tailwind css", "tailwindcss"],
            "sass": ["sass", "scss"],
            "less": ["less"],
            "webpack": ["webpack"],
            "babel": ["babel"],
            "jest": ["jest", "jest testing"],
            "mocha": ["mocha", "mocha testing"],
            "cypress": ["cypress", "cypress testing"],
            "selenium": ["selenium", "selenium webdriver"],
            
            # databases
            "mysql": ["mysql", "mariadb"],
            "postgresql": ["postgresql", "postgres", "psql"],
            "mongodb": ["mongodb", "mongo"],
            "redis": ["redis"],
            "elasticsearch": ["elasticsearch", "elastic search"],
            "dynamodb": ["dynamodb", "dynamo db"],
            "firebase": ["firebase", "firestore"],
            "sqlite": ["sqlite", "sqlite3"],
            
            # cloud platforms
            "aws": ["aws", "amazon web services", "amazon aws"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud platform", "google cloud"],
            "heroku": ["heroku"],
            "vercel": ["vercel"],
            "netlify": ["netlify"],
            "digitalocean": ["digitalocean", "digital ocean"],
            
            # tools and utilities
            "git": ["git", "github", "gitlab", "bitbucket"],
            "docker": ["docker", "docker container"],
            "kubernetes": ["kubernetes", "k8s"],
            "jenkins": ["jenkins", "ci/cd"],
            "github actions": ["github actions", "github ci"],
            "gitlab ci": ["gitlab ci", "gitlab pipeline"],
            "travis ci": ["travis ci", "travis"],
            "circleci": ["circleci", "circle ci"],
            "vscode": ["vscode", "visual studio code"],
            "intellij": ["intellij", "intellij idea"],
            "eclipse": ["eclipse"],
            "vim": ["vim", "vi"],
            "emacs": ["emacs"],
            "postman": ["postman"],
            "insomnia": ["insomnia"],
            "swagger": ["swagger", "openapi"],
            
            # methodologies
            "agile": ["agile", "scrum", "kanban"],
            "scrum": ["scrum", "agile scrum"],
            "kanban": ["kanban"],
            "tdd": ["tdd", "test driven development"],
            "bdd": ["bdd", "behavior driven development"],
            "devops": ["devops", "dev ops"],
            "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
            "microservices": ["microservices", "micro service"],
            "rest": ["rest", "restful", "rest api"],
            "graphql": ["graphql", "graph ql"],
            "soap": ["soap", "soap api"],
            "oauth": ["oauth", "oauth 2.0"],
            "jwt": ["jwt", "json web token"],
            
            # soft skills
            "leadership": ["leadership", "lead", "team lead"],
            "communication": ["communication", "communicate"],
            "problem solving": ["problem solving", "problem-solving", "problem solve"],
            "teamwork": ["teamwork", "team work", "collaboration"],
            "project management": ["project management", "project manager"],
            "mentoring": ["mentoring", "mentor"],
            "presentation": ["presentation", "present"],
            "documentation": ["documentation", "document"],
        }
        
        # reverse mapping for quick lookup
        self.reverse_mappings = {}
        for normalized, variations in self.skill_mappings.items():
            for variation in variations:
                self.reverse_mappings[variation.lower()] = normalized
    
    def extract_skills_from_resume(self, resume_text: str) -> SkillsData:
        """Extract skills from resume text using enhanced detection."""
        
        print("🔍 Extracting skills from resume text...")
        
        # normalize text for better matching
        normalized_text = resume_text.lower()
        
        # extract skills using multiple methods
        detected_skills = set()
        
        # method 1: direct skill mapping
        for variation, normalized in self.reverse_mappings.items():
            if variation in normalized_text:
                detected_skills.add(normalized)
        
        # method 2: regex patterns for common skill sections
        skill_patterns = [
            r'skills?[:\s]*([^.\n]+)',
            r'technologies?[:\s]*([^.\n]+)',
            r'programming languages?[:\s]*([^.\n]+)',
            r'frameworks?[:\s]*([^.\n]+)',
            r'tools?[:\s]*([^.\n]+)',
            r'technologies?[:\s]*([^.\n]+)',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, normalized_text, re.IGNORECASE)
            for match in matches:
                # split by common separators
                skills = re.split(r'[,;•\-\|]', match)
                for skill in skills:
                    skill = skill.strip()
                    if skill and len(skill) > 2:
                        # try to normalize
                        normalized = self.reverse_mappings.get(skill.lower(), skill.lower())
                        detected_skills.add(normalized)
        
        # method 3: look for capitalized technical terms
        tech_terms = re.findall(r'\b[A-Z][a-z]+(?:\.[A-Z][a-z]+)*\b', resume_text)
        for term in tech_terms:
            if term.lower() in self.reverse_mappings:
                detected_skills.add(self.reverse_mappings[term.lower()])
        
        # categorize skills
        categorized_skills = self._categorize_skills(list(detected_skills))
        
        return SkillsData(
            programming_languages=categorized_skills["programming_languages"],
            frameworks=categorized_skills["frameworks"],
            databases=categorized_skills["databases"],
            cloud_platforms=categorized_skills["cloud_platforms"],
            tools=categorized_skills["tools"],
            methodologies=categorized_skills["methodologies"],
            soft_skills=categorized_skills["soft_skills"],
            all_skills=list(detected_skills),
            skill_count=len(detected_skills)
        )
    
    def extract_skills_from_github(self, github_data: Dict[str, Any]) -> SkillsData:
        """Extract skills from GitHub profile and repository data."""
        
        print("🔍 Extracting skills from GitHub data...")
        
        detected_skills = set()
        
        # extract from repositories
        if "repositories" in github_data:
            for repo in github_data["repositories"]:
                # languages used in repositories
                if "languages" in repo:
                    for lang in repo["languages"]:
                        normalized = self.reverse_mappings.get(lang.lower(), lang.lower())
                        detected_skills.add(normalized)
                
                # technologies mentioned in descriptions
                if "description" in repo and repo["description"]:
                    desc = repo["description"].lower()
                    for variation, normalized in self.reverse_mappings.items():
                        if variation in desc:
                            detected_skills.add(normalized)
                
                # topics/tags
                if "topics" in repo:
                    for topic in repo["topics"]:
                        normalized = self.reverse_mappings.get(topic.lower(), topic.lower())
                        detected_skills.add(normalized)
        
        # extract from profile data
        if "top_languages" in github_data:
            for lang in github_data["top_languages"]:
                normalized = self.reverse_mappings.get(lang.lower(), lang.lower())
                detected_skills.add(normalized)
        
        # categorize skills
        categorized_skills = self._categorize_skills(list(detected_skills))
        
        return SkillsData(
            programming_languages=categorized_skills["programming_languages"],
            frameworks=categorized_skills["frameworks"],
            databases=categorized_skills["databases"],
            cloud_platforms=categorized_skills["cloud_platforms"],
            tools=categorized_skills["tools"],
            methodologies=categorized_skills["methodologies"],
            soft_skills=categorized_skills["soft_skills"],
            all_skills=list(detected_skills),
            skill_count=len(detected_skills)
        )
    
    def combine_skills(self, resume_skills: SkillsData, github_skills: SkillsData) -> SkillsData:
        """Combine skills from resume and GitHub data."""
        
        print("🔗 Combining skills from resume and GitHub...")
        
        # combine all skills
        all_resume_skills = set(resume_skills.all_skills)
        all_github_skills = set(github_skills.all_skills)
        combined_skills = all_resume_skills.union(all_github_skills)
        
        # categorize combined skills
        categorized_skills = self._categorize_skills(list(combined_skills))
        
        return SkillsData(
            programming_languages=categorized_skills["programming_languages"],
            frameworks=categorized_skills["frameworks"],
            databases=categorized_skills["databases"],
            cloud_platforms=categorized_skills["cloud_platforms"],
            tools=categorized_skills["tools"],
            methodologies=categorized_skills["methodologies"],
            soft_skills=categorized_skills["soft_skills"],
            all_skills=list(combined_skills),
            skill_count=len(combined_skills)
        )
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different types."""
        
        categories = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_platforms": [],
            "tools": [],
            "methodologies": [],
            "soft_skills": []
        }
        
        # programming languages
        programming_langs = ["javascript", "python", "java", "c++", "c#", "php", "ruby", 
                           "go", "rust", "swift", "kotlin", "typescript", "scala", "r", "matlab", "sql"]
        
        # frameworks
        framework_list = ["react", "angular", "vue", "express", "django", "flask", "spring", 
                         "laravel", "asp.net", "jquery", "bootstrap", "tailwind", "sass", "less"]
        
        # databases
        database_list = ["mysql", "postgresql", "mongodb", "redis", "elasticsearch", 
                        "dynamodb", "firebase", "sqlite"]
        
        # cloud platforms
        cloud_list = ["aws", "azure", "gcp", "heroku", "vercel", "netlify", "digitalocean"]
        
        # tools
        tools_list = ["git", "docker", "kubernetes", "jenkins", "github actions", "gitlab ci", 
                     "travis ci", "circleci", "vscode", "intellij", "eclipse", "vim", "emacs", 
                     "postman", "insomnia", "swagger"]
        
        # methodologies
        methodology_list = ["agile", "scrum", "kanban", "tdd", "bdd", "devops", "ci/cd", 
                           "microservices", "rest", "graphql", "soap", "oauth", "jwt"]
        
        # soft skills
        soft_skills_list = ["leadership", "communication", "problem solving", "teamwork", 
                           "project management", "mentoring", "presentation", "documentation"]
        
        # categorize each skill
        for skill in skills:
            if skill in programming_langs:
                categories["programming_languages"].append(skill)
            elif skill in framework_list:
                categories["frameworks"].append(skill)
            elif skill in database_list:
                categories["databases"].append(skill)
            elif skill in cloud_list:
                categories["cloud_platforms"].append(skill)
            elif skill in tools_list:
                categories["tools"].append(skill)
            elif skill in methodology_list:
                categories["methodologies"].append(skill)
            elif skill in soft_skills_list:
                categories["soft_skills"].append(skill)
            else:
                # default to tools if not categorized
                categories["tools"].append(skill)
        
        return categories
