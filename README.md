# HireBuddy - AI-Powered Hiring Assistant

<div align="center">
  
[![Demo Video](https://img.shields.io/badge/🎥_Demo-Watch_on_YouTube-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=ABo2hvASLmk)
[![Python](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Portia AI](https://img.shields.io/badge/Powered_by-Portia_AI-purple?style=for-the-badge)](https://portialabs.ai)

*Intelligent recruitment automation - from resume parsing to interview scheduling*

</div>

## Live Demo (Click to Watch)

[![Watch HireBuddy in Action](https://img.youtube.com/vi/ABo2hvASLmk/hqdefault.jpg)](https://www.youtube.com/watch?v=ABo2hvASLmk "HireBuddy End-to-End Demo")

End‑to‑end automated hiring workflow in under 5 minutes (click thumbnail to watch).

## What is HireBuddy?

HireBuddy is a lean AI agent system that turns an uploaded resume + job description into a scored, evidence‑backed hiring decision (and optional scheduled interview) in minutes.

**Problem**
Early‑stage screening is slow, subjective, and fragmented:
- Manual resume parsing is repetitive
- GitHub review (if done) is shallow or skipped
- Match rationale is rarely documented
- Scheduling and email follow‑ups burn time

**Crux**
Hiring teams need fast, consistent, explainable evaluation without adding another bloated platform.

**Solution**
Multi‑agent workflow (Resume, GitHub, Matching, Scheduler) powered by Portia AI:
- Extracts structured candidate profile
- Performs deep GitHub repo + activity relevance analysis
- Generates transparent weighted match score with reasons
- Streams every step for trust (no hidden black box)
- Optionally drafts emails & books the interview

**How It Solves It**
Automation compresses hours of fragmented manual work into a single deterministic flow: ingest → enrich → score → decide → communicate. Standardized scoring + captured rationale reduce bias and create an auditable trail while preserving recruiter judgment at the decision gate.

## System Architecture

![Architecture Diagram](arch.png)

### Architecture Walkthrough Video (Click to Watch)

[![Architecture Deep Dive](https://img.youtube.com/vi/gjOww3AcLLw/hqdefault.jpg)](https://www.youtube.com/watch?v=gjOww3AcLLw "Architecture Deep Dive")

Short video explaining agent orchestration, data flow, and scoring pipeline.

HireBuddy uses a multi-agent architecture where specialized AI agents collaborate:

- **Resume Agent** - Extracts structured data from any resume format using LLM parsing
- **GitHub Agent** - Performs deep analysis of coding profiles, repositories, and contribution patterns  
- **Supervisor Agent** - Orchestrates the workflow and makes intelligent routing decisions
- **Scheduler Agent** - Handles interview scheduling with Google Calendar and email automation

Each agent specializes in their domain while the supervisor coordinates the entire evaluation process.

## Portia AI Core (How We Use It)

Portia AI is the backbone of this project. Every agent you see (planner/supervisor, resume, GitHub, scheduler) is a Portia agent. Portia handles:
- Orchestrating the exact order of steps (no ad‑hoc scripts)
- Passing structured outputs from one agent/tool to the next (shared context)
- Managing tool calls (so code just declares intent, not plumbing)
- Streaming intermediate status so the UI shows real progress
- Containing failures (a later step can still run if an earlier non‑critical tool partially fails)

### Where Portia AI Is Used in the Flow
1. Upload → planner stores raw files in context
2. Resume parsing tool -> structured candidate profile added to context
3. GitHub scan tool -> repos, languages, activity added
4. Matching + assessment tools -> scores + reasoning objects
5. Decision + email/scheduling -> scheduler tool prepares calendar + message artifacts
6. Tracking tool appends final decision for audit

### Portia Agent Roles (Plain Words)
- Planner: decides next step, merges results, builds the final narrative
- Resume Agent: extracts clean structured data (skills, experience, education)
- GitHub Agent: pulls profile + repos + contribution signals, filters relevance
- Scheduler Agent: prepares interview invite artifacts (email text, calendar details)

### Tools We Call Through Portia
- resume_parser: multi‑library text extraction + normalization
- github_scanner: GraphQL + heuristic repo relevance & activity metrics
- job_matcher: compares candidate skill/profile vectors to job requirements
- assessment_generator: composes weighted scoring + reasoning breakdown
- candidate_tracker: persists decision row (CSV/JSON)
- code / repository analyzers (where enabled): language spread, complexity hints
- calendar/email integration (via scheduler) for final scheduling output

### Why Portia Fits Here
Simple: we needed a clean multi‑agent pipeline without writing custom orchestration glue. Portia gives shared state, consistent tool wiring, retry hooks, and streaming out of the box—so we focus on the actual evaluation logic instead of framework code.

## Core Features

### Intelligent Resume Analysis
- **Universal Format Support** - Handles PDF, DOCX, and text files with advanced parsing
- **LLM-Powered Extraction** - Uses AI models to understand context and extract relevant information
- **Structured Output** - Converts unstructured resumes into standardized candidate profiles
- **Smart Field Recognition** - Automatically categorizes skills, experience levels, and project complexity

### Advanced GitHub Analysis  
- **Repository Intelligence** - Analyzes code quality, project complexity, and documentation standards
- **Job-Specific Filtering** - Identifies repositories most relevant to the target role
- **Activity Pattern Assessment** - Evaluates coding consistency, contribution frequency, and collaboration
- **Technology Stack Mapping** - Maps programming languages and frameworks to job requirements
- **Code Quality Metrics** - Assesses best practices, project structure, and community engagement

### Smart Job Matching
- **AI-Powered Scoring** - Multi-dimensional analysis considering skills, experience, and GitHub activity
- **Weighted Evaluation** - Customizable criteria weights based on role importance
- **Detailed Breakdowns** - Transparent scoring with specific reasoning for each component
- **Actionable Insights** - Clear recommendations for hiring decisions

### Automated Workflow
- **Real-time Processing** - Live streaming of analysis progress with detailed step updates
- **Email Generation** - Personalized candidate and manager notifications with customizable templates
- **Interview Scheduling** - Automatic Google Calendar integration with Meet links
- **Decision Tracking** - Complete audit trail of all hiring decisions and interactions

## How It Works

### 1. File Upload
Users upload candidate resumes and job descriptions through the web interface. The system supports multiple formats and provides real-time validation.

### 2. Resume Analysis
The Resume Agent uses LLM models to extract structured data:
- Personal information and contact details
- Work experience with role descriptions and durations
- Educational background and certifications
- Skills categorized by type and proficiency
- Projects with technology stacks and descriptions

### 3. GitHub Profile Analysis
If a GitHub profile is found, the GitHub Agent performs:
- Repository scanning with relevance scoring
- Code quality assessment based on documentation, structure, and community engagement
- Contribution pattern analysis for consistency and activity levels
- Technology stack identification and mapping to job requirements
- Project complexity evaluation

### 4. Job Matching & Scoring
The system performs intelligent matching:
- **Required Skills Match** (40% weight) - How well candidate skills align with must-have requirements
- **Experience Alignment** (25% weight) - Relevance of work experience to the role
- **GitHub Activity** (20% weight) - Quality and consistency of coding contributions
- **Education Background** (15% weight) - Educational qualifications and certifications

### 5. Decision & Scheduling
Based on the analysis, recruiters can:
- Review detailed candidate insights and match scores
- Make informed hiring decisions with AI recommendations
- Automatically generate personalized interview invitations
- Schedule interviews with Google Calendar integration
- Track all decisions for analytics and improvement

## Sample Analysis Output

### Candidate Profile Analysis
```json
{
  "candidate_name": "Sarah Chen",
  "email": "sarah.chen@email.com",
  "github": "https://github.com/sarahdev",
  "experience_years": 3,
  "skills": {
    "programming_languages": ["Python", "JavaScript", "TypeScript"],
    "frameworks": ["React", "Django", "FastAPI"],
    "tools": ["Git", "Docker", "AWS", "PostgreSQL"]
  },
  "projects_count": 8,
  "education": "MS Computer Science"
}
```

### GitHub Analysis Results
```json
{
  "github_analysis": {
    "username": "sarahdev",
    "public_repos": 22,
    "total_contributions": 1340,
    "activity_level": "High",
    "top_languages": ["Python", "JavaScript", "TypeScript"],
    "relevant_repositories": [
      {
        "name": "react-dashboard-app",
        "relevance_score": 0.92,
        "languages": ["TypeScript", "React"],
        "complexity": "Medium-High",
        "stars": 89,
        "quality_indicators": ["Good documentation", "Active maintenance", "Clean code structure"]
      }
    ],
    "coding_patterns": ["Modern JavaScript practices", "Component-based architecture", "Test-driven development"]
  }
}
```

### Job Match Scoring
```json
{
  "match_analysis": {
    "overall_score": 0.84,
    "score_breakdown": {
      "required_skills": 0.88,
      "experience_level": 0.82,
      "github_activity": 0.91,
      "education": 0.75
    },
    "strengths": [
      "Strong proficiency in required technologies (React, TypeScript)",
      "Active GitHub presence with quality projects",
      "Recent experience with similar tech stack"
    ],
    "recommendations": [
      "Excellent technical candidate - proceed with interview",
      "Focus interview on system design and scalability",
      "Discuss react-dashboard-app project in detail"
    ]
  }
}
```

## Quick Start

### Prerequisites
- Python 3.13+
- Git
- Google account (for calendar integration)
- GitHub account (for repository analysis)

### Installation

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/HireBuddy.git
   cd HireBuddy
   
   # Install UV package manager (recommended)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Install dependencies
   uv sync
   
   # Activate virtual environment
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   # Required: Google AI API Key (get from https://aistudio.google.com/)
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Required: GitHub Token (get from https://github.com/settings/tokens)
   GITHUB_TOKEN=your_github_personal_access_token
   
   # Required: Portia API Key (get from https://app.portialabs.ai/)
   PORTIA_API_KEY=your_portia_api_key_here
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```
   
   Open `http://localhost:5000` in your browser.

### API Key Setup

**Google AI API Key**
- Visit [Google AI Studio](https://aistudio.google.com/)
- Create/select project and generate API key
- Note: Free tier has 200 requests/day limit

**GitHub Personal Access Token**  
- Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
- Generate token with `public_repo`, `read:user`, `user:email` scopes

**Portia API Key**
- Visit [Portia Labs](https://app.portialabs.ai/)
- Create account and generate API key for email/calendar features

## Project Structure

```
HireBuddy/
├── app.py                      # Flask web application
├── main.py                     # CLI entry point
├── agents/                     # AI agent implementations
│   ├── planner_agent.py        # Main workflow orchestrator
│   ├── github_agent.py         # GitHub analysis specialist
│   ├── resume_agent.py         # Resume parsing agent
│   └── scheduler_agent.py      # Interview scheduling agent
├── tools/                      # Core analysis tools
│   ├── github_scanner.py       # GitHub API integration
│   ├── resume_parser.py        # Multi-format resume parsing
│   ├── job_matcher.py          # Candidate-job alignment
│   ├── assessment_generator.py # Comprehensive evaluation engine
│   └── candidate_tracker.py    # Decision tracking and analytics
├── utils/                      # Data models and utilities
│   └── schemas.py              # Pydantic data models
├── templates/                  # Web interface
│   └── index.html              # Modern responsive UI
└── output/                     # Analysis results and tracking
```

## Technical Implementation

### Resume Processing Pipeline
HireBuddy uses a multi-layered approach for resume parsing:
1. **Format Detection** - Automatically identifies PDF, DOCX, or text formats
2. **Text Extraction** - Uses multiple libraries (PyPDF2, pdfplumber, PyMuPDF) for robust extraction
3. **LLM Analysis** - Gemini/GPT models parse unstructured text into structured data
4. **Data Validation** - Pydantic models ensure data quality and consistency

### GitHub Analysis Engine
The GitHub analysis combines API data with intelligent processing:
1. **Profile Scanning** - Retrieves comprehensive profile and repository data
2. **Repository Filtering** - Identifies relevant repositories based on job requirements
3. **Code Quality Assessment** - Analyzes documentation, structure, and best practices
4. **Activity Pattern Recognition** - Evaluates contribution consistency and collaboration

### Intelligent Matching Algorithm
The matching system uses weighted scoring across multiple dimensions:
- **Skill Alignment** - Fuzzy matching between candidate skills and job requirements
- **Experience Relevance** - Contextual analysis of work experience descriptions
- **GitHub Quality Score** - Repository quality, activity level, and code patterns
- **Cultural Fit Indicators** - Communication style, project types, and collaboration patterns

## Why HireBuddy?

### For Recruiters
- **Time Savings** - Reduce resume screening time from hours to minutes
- **Consistent Evaluation** - Eliminate human bias with standardized AI analysis
- **Better Insights** - GitHub analysis provides deeper technical assessment
- **Automated Workflow** - From analysis to interview scheduling in one platform

### For Hiring Managers  
- **Data-Driven Decisions** - Detailed scoring and reasoning for each candidate
- **Technical Validation** - Comprehensive GitHub analysis for technical roles
- **Streamlined Process** - Automated scheduling and communication
- **Audit Trail** - Complete tracking of all hiring decisions

### For Candidates
- **Fair Evaluation** - Standardized analysis reduces unconscious bias
- **GitHub Recognition** - Open source contributions are properly evaluated
- **Professional Communication** - Automated, personalized interview invitations
- **Transparent Process** - Clear insights into evaluation criteria

## Contributing

We welcome contributions to improve HireBuddy! Areas of focus:
- **New Integrations** - ATS systems, job boards, assessment platforms
- **Enhanced Analysis** - Additional code quality metrics, skill detection
- **UI/UX Improvements** - Frontend enhancements and user experience
- **Performance Optimization** - Analysis speed and accuracy improvements

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with [Portia AI](https://portialabs.ai/) for multi-agent orchestration, powered by Google's Gemini models for intelligent analysis, and integrated with GitHub's comprehensive API for repository insights.
