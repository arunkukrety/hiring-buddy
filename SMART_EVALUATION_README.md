# Smart Candidate Evaluation System

A comprehensive, AI-powered candidate evaluation system that intelligently matches candidates to job positions using resume analysis, GitHub profile evaluation, and transparent scoring.

## 🎯 Overview

This system implements a multi-agent architecture that:

1. **Parses Job Descriptions** - Intelligently extracts requirements, skills, and technologies
2. **Analyzes Resumes** - Extracts candidate information using LLM-powered parsing
3. **Evaluates GitHub Profiles** - Focuses on job-relevant repositories and code quality
4. **Provides Transparent Scoring** - Delivers detailed breakdowns with clear reasoning
5. **Generates Recommendations** - Offers actionable insights for hiring decisions

## 🏗️ System Architecture

### Core Agents

#### 1. **Job Parser Agent** (`agents/job_parser_agent.py`)
- Parses job description files using LLM analysis
- Extracts required/preferred skills, technologies, and experience
- Identifies role type, seniority level, and industry focus
- Assigns importance weights to different requirements

#### 2. **Enhanced GitHub Agent** (`agents/enhanced_github_agent.py`)
- Filters repositories based on job relevance
- Analyzes code quality and project complexity
- Detects frameworks and technologies used
- Evaluates contribution patterns and community engagement

#### 3. **Candidate Evaluator Agent** (`agents/candidate_evaluator_agent.py`)
- Orchestrates the entire evaluation workflow
- Performs comprehensive skill matching
- Generates transparent scoring with detailed breakdowns
- Provides actionable recommendations

### Data Models

#### Job Description Schema
```python
class JobDescription(BaseModel):
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    technologies: List[str]
    frameworks: List[str]
    role_type: str
    seniority_level: str
    requirements: List[JobRequirement]  # with weights
```

#### Candidate Evaluation Schema
```python
class CandidateEvaluation(BaseModel):
    overall_score: float  # 0-100
    probability_fit: float  # 0-1
    categories: List[EvaluationCategory]  # detailed breakdown
    skill_matches: List[SkillMatch]  # skill-by-skill analysis
    relevant_repositories: List[RepositoryAnalysis]
    key_strengths: List[str]
    key_concerns: List[str]
    recommendations: List[str]
    evaluation_reasoning: str
    confidence_level: str
```

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
uv sync

# Ensure you have API keys configured
cp env.example .env
# Edit .env with your API keys
```

### 2. Prepare Files
```bash
# Place your resume
cp your_resume.pdf resume.pdf

# Create job description (or use sample)
python smart_evaluation.py  # Creates sample job_description.txt
# Edit job_description.txt with your requirements
```

### 3. Run Evaluation
```bash
python smart_evaluation.py
```

## 📋 Job Description Format

Create a `job_description.txt` file with your requirements:

```markdown
# Senior Frontend Developer

## Required Skills
- JavaScript (ES6+)
- React.js
- HTML5 & CSS3
- Git version control

## Preferred Skills
- TypeScript
- Next.js
- Tailwind CSS
- Unit testing

## Experience Requirements
- 3+ years of frontend development
- Experience with modern frameworks

## Technologies We Use
- React.js
- TypeScript
- Next.js
- GraphQL
```

## 📊 Output Example

```
============================================================
SMART CANDIDATE EVALUATION RESULTS
============================================================

🎯 Candidate: John Doe
📋 Position: Senior Frontend Developer
📊 Overall Score: 78.5/100
🎲 Probability of Fit: 78.5%
🔍 Confidence Level: High

📈 CATEGORY BREAKDOWN:
  • Skills Match: 85.0/100 (Weight: 0.4)
  • Experience Relevance: 72.0/100 (Weight: 0.3)
  • GitHub Analysis: 82.0/100 (Weight: 0.3)

💪 KEY STRENGTHS:
  • Strong JavaScript and React.js skills
  • Active GitHub profile with relevant projects
  • Experience with modern frontend frameworks

🔍 DETAILED SKILL MATCHES:
  ✅ JavaScript (REQUIRED) - Score: 0.9
    • Listed as primary skill in resume
    • Multiple JavaScript projects on GitHub
  ✅ React.js (REQUIRED) - Score: 0.8
    • 2 years experience mentioned
    • React projects in portfolio

🐙 RELEVANT REPOSITORIES (3 found):
  📁 react-ecommerce-app (Relevance: 0.85)
    • Languages: JavaScript, CSS, HTML
    • Complexity: Medium complexity - Substantial project
    • Quality: Has README documentation, Active development
```

## 🔧 Configuration

### Environment Variables
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
GITHUB_TOKEN=your_github_token  # Optional, for enhanced GitHub analysis
```

### Customization Options

#### Scoring Weights
Modify the evaluation weights in `agents/candidate_evaluator_agent.py`:
```python
# Default weights
SKILLS_WEIGHT = 0.4
EXPERIENCE_WEIGHT = 0.3
GITHUB_WEIGHT = 0.3
```

#### Repository Relevance Threshold
Adjust the minimum relevance score in `agents/enhanced_github_agent.py`:
```python
# Only include repositories with relevance > 0.1
if relevance_score > 0.1:
    relevant_repos.append(repo)
```

## 🎛️ Advanced Features

### 1. **Intelligent Repository Filtering**
- Automatically identifies job-relevant repositories
- Calculates relevance scores based on:
  - Language overlap with job requirements
  - Framework/technology mentions
  - Project complexity and activity
  - Community engagement (stars, forks)

### 2. **Transparent Scoring**
- Detailed breakdown by category
- Skill-by-skill matching with evidence
- Confidence levels for each assessment
- Clear reasoning for scores

### 3. **Multi-Format Support**
- PDF resumes (with multiple parsing methods)
- Text-based job descriptions
- Various GitHub URL formats
- Structured JSON output

### 4. **Extensible Architecture**
- Modular agent system
- Easy to add new evaluation criteria
- Configurable scoring algorithms
- Pluggable data sources

## 📁 File Structure

```
GithubPortia/
├── smart_evaluation.py              # Main entry point
├── job_description.txt              # Job requirements
├── resume.pdf                       # Candidate resume
├── agents/
│   ├── job_parser_agent.py         # Job description parser
│   ├── enhanced_github_agent.py    # GitHub analysis
│   ├── candidate_evaluator_agent.py # Main evaluator
│   └── ...
├── utils/
│   └── schemas.py                   # Data models
├── output/                          # Evaluation results
└── SMART_EVALUATION_README.md       # This file
```

## 🔍 Evaluation Criteria

### Skills Assessment (40% weight)
- **Required Skills**: Must-have skills for the role
- **Preferred Skills**: Nice-to-have skills
- **Skill Evidence**: Verification from resume and GitHub

### Experience Evaluation (30% weight)
- **Relevance**: How well experience matches job requirements
- **Duration**: Years of relevant experience
- **Quality**: Depth and breadth of experience

### GitHub Analysis (30% weight)
- **Repository Relevance**: How well projects match job requirements
- **Code Quality**: Documentation, activity, community engagement
- **Technical Depth**: Complexity and sophistication of projects
- **Contribution Patterns**: Active development and collaboration

## 🚨 Troubleshooting

### Common Issues

1. **"Job description file not found"**
   - Ensure `job_description.txt` exists in project root
   - Run `python smart_evaluation.py` to create sample

2. **"Resume file not found"**
   - Place resume as `resume.pdf` in project root
   - Ensure file is readable and not corrupted

3. **"GitHub scanner not available"**
   - Set `GITHUB_TOKEN` in environment variables
   - Or the system will work without GitHub analysis

4. **"API key not configured"**
   - Set required API keys in `.env` file
   - At minimum, set `OPENAI_API_KEY`

### Debug Mode
Add debug logging by modifying the agent files to include more detailed output.

## 🔮 Future Enhancements

### Planned Features
1. **LinkedIn Integration** - Professional network analysis
2. **Portfolio Analysis** - Website and project portfolio evaluation
3. **Interview Preparation** - Generate interview questions based on gaps
4. **Comparative Analysis** - Rank multiple candidates
5. **Custom Scoring Models** - Industry-specific evaluation criteria

### Extensibility
The modular architecture makes it easy to add:
- New data sources (LinkedIn, portfolio sites)
- Custom evaluation criteria
- Industry-specific scoring models
- Integration with ATS systems

## 📝 License

[Add your license information here]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built with Portia AI** - The intelligent planning and execution framework for AI agents.
