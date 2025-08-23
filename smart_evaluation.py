"""Smart Candidate Evaluation System - Main Entry Point

This script implements a comprehensive candidate evaluation system that:
1. Parses job descriptions to understand requirements
2. Analyzes candidate resumes for skills and experience
3. Evaluates GitHub profiles for technical capabilities
4. Provides transparent scoring and recommendations
"""

import sys
from pathlib import Path

from portia import Portia, Config
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput
from portia.tools import DefaultToolRegistry
from portia.execution_hooks import CLIExecutionHooks

from agents.candidate_evaluator_agent import CandidateEvaluatorAgent


def main():
    """Main function for smart candidate evaluation."""
    
    print("🚀 Smart Candidate Evaluation System")
    print("=" * 50)
    
    # check if job description file exists
    job_description_path = "job_description.txt"
    if not Path(job_description_path).exists():
        print(f"❌ Error: Job description file '{job_description_path}' not found!")
        print("Please create a job_description.txt file with the job requirements.")
        return
    
    # check if resume file exists
    resume_path = "resume.pdf"
    if not Path(resume_path).exists():
        print(f"❌ Error: Resume file '{resume_path}' not found!")
        print("Please place your resume as 'resume.pdf' in the project root.")
        return
    
    try:
        # initialize portia
        print("🔧 Initializing Portia AI system...")
        config = Config.from_default()
        portia = Portia(
            config=config,
            tools=DefaultToolRegistry(config=config),
            execution_hooks=CLIExecutionHooks(),
        )
        
        # create candidate evaluator agent
        print("🤖 Creating candidate evaluator agent...")
        evaluator = CandidateEvaluatorAgent(portia)
        
        # perform comprehensive evaluation
        print("🎯 Starting comprehensive candidate evaluation...")
        evaluation = evaluator.evaluate_candidate_for_job(resume_path, job_description_path)
        
        # display results
        print("\n" + "=" * 60)
        print("SMART CANDIDATE EVALUATION RESULTS")
        print("=" * 60)
        
        # display evaluation summary
        summary = evaluator.get_evaluation_summary(evaluation)
        print(summary)
        
        # display detailed skill matches
        if evaluation.skill_matches:
            print("🔍 DETAILED SKILL MATCHES:")
            for skill_match in evaluation.skill_matches:
                status = "✅" if skill_match.candidate_has else "❌"
                importance = "REQUIRED" if skill_match.required else "PREFERRED"
                print(f"  {status} {skill_match.skill} ({importance}) - Score: {skill_match.match_score:.1f}")
                if skill_match.evidence:
                    for evidence in skill_match.evidence[:2]:  # show first 2 pieces of evidence
                        print(f"    • {evidence}")
        
        # display relevant repositories
        if evaluation.relevant_repositories:
            print(f"\n🐙 RELEVANT REPOSITORIES ({len(evaluation.relevant_repositories)} found):")
            for repo in evaluation.relevant_repositories[:5]:  # show top 5
                print(f"  📁 {repo.name} (Relevance: {repo.relevance_score:.1f})")
                print(f"    • Languages: {', '.join(repo.languages_used[:3])}")
                print(f"    • Complexity: {repo.project_complexity}")
                if repo.code_quality_indicators:
                    print(f"    • Quality: {', '.join(repo.code_quality_indicators[:2])}")
        
        print("\n" + "=" * 60)
        print("✅ Smart evaluation completed successfully!")
        print("📊 Results saved to output/ directory")
        print("🤖 This system provides transparent, AI-powered candidate assessment")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def create_sample_job_description():
    """Create a sample job description for testing."""
    
    sample_job = """# Senior Frontend Developer

## About the Role
We are looking for a Senior Frontend Developer to join our dynamic team. You will be responsible for building and maintaining high-quality web applications using modern frontend technologies.

## Required Skills
- JavaScript (ES6+)
- React.js
- HTML5 & CSS3
- Git version control
- Responsive web design
- RESTful APIs

## Preferred Skills
- TypeScript
- Next.js
- Tailwind CSS
- GraphQL
- Unit testing (Jest, React Testing Library)
- CI/CD pipelines

## Experience Requirements
- 3+ years of frontend development experience
- Experience with modern JavaScript frameworks
- Experience with responsive design principles
- Experience with version control systems

## Preferred Experience
- Experience with TypeScript
- Experience with server-side rendering
- Experience with performance optimization
- Experience with accessibility standards

## Technologies We Use
- React.js
- TypeScript
- Next.js
- Tailwind CSS
- GraphQL
- Jest
- GitHub Actions

## Responsibilities
- Develop and maintain web applications
- Collaborate with design and backend teams
- Write clean, maintainable code
- Participate in code reviews
- Mentor junior developers
"""
    
    with open("job_description.txt", "w", encoding="utf-8") as f:
        f.write(sample_job)
    
    print("📝 Sample job description created in job_description.txt")
    print("You can edit this file with your specific job requirements.")


if __name__ == "__main__":
    # check if job description exists, create sample if not
    if not Path("job_description.txt").exists():
        print("📝 No job description found. Creating sample job description...")
        create_sample_job_description()
        print("\nPlease edit job_description.txt with your specific requirements, then run again.")
        sys.exit(0)
    
    main()
