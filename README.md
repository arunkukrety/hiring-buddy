# Recruiting Agent - LLM-Powered Resume Parser

A dynamic resume analysis system built with Portia AI that can parse any resume format using LLM-based extraction.

## 🚀 Features

- **Universal Resume Support**: Handles PDF, LaTeX, and text-based resumes
- **LLM-Powered Parsing**: Uses advanced language models for accurate information extraction
- **GitHub Profile Analysis**: Comprehensive GitHub activity and code analysis
- **Structured Output**: Returns standardized JSON with candidate information
- **Robust PDF Processing**: Multiple fallback methods for PDF text extraction
- **Portia AI Integration**: Built on Portia's planning and execution framework

## 📋 Extracted Information

### Resume Data
- **Personal Details**: Name, email, phone, location
- **Professional Links**: LinkedIn, GitHub, portfolio
- **Education**: Schools, degrees, dates
- **Experience**: Companies, titles, descriptions, dates
- **Skills**: Categorized as primary, secondary, and tools
- **Projects**: Names, descriptions, tech stacks, links

### GitHub Analysis
- **Profile Information**: Name, bio, location, company, website
- **Activity Metrics**: Public repos, followers, following, account age
- **Code Analysis**: Programming languages used, commit frequency
- **Project Assessment**: Consistency, collaboration level, code quality
- **Technical Depth**: Overall activity score and technical assessment

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd GithubPortia
   ```

2. **Set up virtual environment**
   ```bash
   uv sync
   ```

3. **Install dependencies**
   ```bash
   pip install PyPDF2 pdfplumber PyMuPDF
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

## 🔧 Usage

### Basic Usage
```bash
python main.py
```

### With Custom Resume
```bash
# Place your resume as resume.pdf in the project root
python main.py
```

### Test GitHub Agent
```bash
# Test GitHub profile analysis functionality
python test_github_agent.py
```

## 📁 Project Structure

```
GithubPortia/
├── main.py                     # Main entry point
├── agents/                     # Agent modules
│   ├── __init__.py
│   ├── llm_resume_parser.py    # LLM-based resume parser
│   ├── planner_agent.py        # Planning agent for analysis
│   ├── github_agent.py         # GitHub profile analysis agent
│   └── resume_agent.py         # Resume analysis logic
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── schemas.py              # Pydantic data models
│   └── cli.py                  # Command-line interface
├── tools/                      # Tool modules
│   ├── __init__.py
│   ├── tools.py                # General tools
│   ├── github_scanner.py       # GitHub profile scanner
│   └── resume_parser.py        # Resume text extractor
├── env.example                 # Environment variables template
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## 🔑 Environment Variables

Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

## 📊 Example Output

```
============================================================
DYNAMIC RESUME ANALYSIS RESULTS
============================================================

📋 Candidate: SWAYAM BANSAL
📧 Email: swayambansal@outlook.com
📱 Phone: +91 9817413427
🐙 GitHub: github.com/swymbnsl/acert-kestra
🌐 Portfolio: www.swymbnsl.com

📊 ANALYSIS SUMMARY:
  • Education: 2 entries found
  • Skills: 25 total skills across categories
  • Projects: 4 projects found

🐙 GITHUB ANALYSIS:
  • Username: octocat
  • Activity Score: 8.5/10
  • Languages: JavaScript, Python, Go
  • Commit Frequency: High
  • Project Consistency: Excellent

🎯 OVERALL ASSESSMENT:
  Strong candidate - Has educational background, Has 3 work experiences, Has 4 projects, Has 9 primary skills

💡 RECOMMENDATIONS:
  1. Consider adding LinkedIn profile
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Built with [Portia AI](https://portialabs.ai/)
- PDF processing with PyPDF2, pdfplumber, and PyMuPDF
