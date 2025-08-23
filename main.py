"""Main entry point for the GitHub Portia system."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from portia import Portia, Config, LLMProvider
from portia.cli import CLIExecutionHooks

from agents import PlannerAgent
from utils.cli import create_sample_job_description


def main():
    """Main function to run the GitHub Portia system."""
    
    # load environment variables
    load_dotenv()
    
    # check required environment variables
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        sys.exit(1)
    
    # initialize portia with Gemini configuration
    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    portia = Portia(config)
    
    # setup execution hooks
    hooks = CLIExecutionHooks()
    
    # get resume path
    resume_path = Path("resume.pdf")
    if not resume_path.exists():
        print(f"❌ Resume file not found: {resume_path}")
        print("Please place your resume as 'resume.pdf' in the current directory")
        sys.exit(1)
    
    # ensure job description exists
    job_description_path = Path("job_description.txt")
    if not job_description_path.exists():
        create_sample_job_description()
        print(f"📝 Created sample job description: {job_description_path}")
        print("You can edit this file to customize the job requirements")
    
    print("🚀 Starting GitHub Portia System")
    print("=" * 50)
    print(f"📄 Resume: {resume_path}")
    print(f"📋 Job Description: {job_description_path}")
    print()
    
    try:
        # create planner agent
        planner = PlannerAgent(portia)
        
        # perform complete analysis
        print("🤖 Starting complete analysis workflow...")
        result = planner.analyze_resume(str(resume_path), str(job_description_path))
        
        # display results
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)
        
        # basic candidate info
        print(f"👤 Candidate: {result.candidate_info.get('candidate_name', 'Unknown')}")
        print(f"📧 Email: {result.candidate_info.get('email', 'N/A')}")
        print(f"📱 Phone: {result.candidate_info.get('phone', 'N/A')}")
        print(f"🔗 GitHub: {result.candidate_info.get('github', 'N/A')}")
        print(f"💼 LinkedIn: {result.candidate_info.get('linkedin', 'N/A')}")
        
        # education summary
        education = result.candidate_info.get('education', [])
        if education:
            print(f"\n🎓 Education ({len(education)} entries):")
            for edu in education[:2]:  # show first 2
                print(f"  • {edu.get('degree', 'N/A')} at {edu.get('school', 'N/A')}")
        
        # experience summary
        experience = result.candidate_info.get('experience', [])
        if experience:
            print(f"\n💼 Experience ({len(experience)} entries):")
            for exp in experience[:2]:  # show first 2
                print(f"  • {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
        
        # skills summary
        skills = result.candidate_info.get('skills', {})
        if skills:
            primary_skills = skills.get('primary', [])
            secondary_skills = skills.get('secondary', [])
            tools = skills.get('tools', [])
            total_skills = len(primary_skills) + len(secondary_skills) + len(tools)
            print(f"\n🛠️ Skills ({total_skills} total):")
            if primary_skills:
                print(f"  • Primary: {', '.join(primary_skills[:5])}")
            if secondary_skills:
                print(f"  • Secondary: {', '.join(secondary_skills[:5])}")
            if tools:
                print(f"  • Tools: {', '.join(tools[:5])}")
        
        # projects summary
        projects = result.candidate_info.get('projects', [])
        if projects:
            print(f"\n📁 Projects ({len(projects)} total):")
            for proj in projects[:3]:  # show first 3
                print(f"  • {proj.get('name', 'N/A')}: {proj.get('description', 'N/A')[:50]}...")
        
        # github analysis
        if result.github_analysis:
            print(f"\n🐙 GitHub Analysis:")
            print(f"  • Username: {result.github_analysis.username}")
            print(f"  • Public Repos: {result.github_analysis.public_repos}")
            print(f"  • Followers: {result.github_analysis.followers}")
            print(f"  • Following: {result.github_analysis.following}")
            
            if result.github_analysis.contributions:
                print(f"  • Total Contributions: {result.github_analysis.contributions.total_contributions}")
                print(f"  • Total Commits: {result.github_analysis.contributions.total_commits}")
                print(f"  • Active Days: {result.github_analysis.contributions.active_days}")
            
            if result.github_analysis.repositories:
                print(f"  • Repositories: {len(result.github_analysis.repositories)}")
                # show top languages
                all_languages = []
                for repo in result.github_analysis.repositories:
                    all_languages.extend(repo.languages)
                if all_languages:
                    from collections import Counter
                    top_languages = Counter(all_languages).most_common(3)
                    print(f"  • Top Languages: {', '.join([lang for lang, _ in top_languages])}")
        
        # job matching results
        if result.job_match_result:
            print(f"\n🎯 Job Matching Results:")
            print(f"  • Position: {result.job_match_result.job_description.title}")
            print(f"  • Match Score: {result.job_match_result.match_score:.1%}")
            print(f"  • Assessment: {result.job_match_result.overall_assessment}")
            
            # display detailed score breakdown if available
            if hasattr(result.job_match_result, 'score_breakdown') and result.job_match_result.score_breakdown:
                print(f"\n📊 Detailed Score Breakdown:")
                breakdown = result.job_match_result.score_breakdown
                for component, details in breakdown["component_scores"].items():
                    score_pct = details["score"] * 100
                    weight_pct = details["weight"] * 100
                    weighted_pct = details["weighted_score"] * 100
                    print(f"  • {component.replace('_', ' ').title()}: {score_pct:.1f}% (Weight: {weight_pct:.0f}% → {weighted_pct:.1f}%)")
                    print(f"    {details['description']}")
                print(f"  • Total Weighted Score: {breakdown['total_weighted_score']*100:.1f}%")
            
            if result.job_match_result.relevant_repositories:
                print(f"  • Relevant Repositories: {len(result.job_match_result.relevant_repositories)}")
                for repo in result.job_match_result.relevant_repositories[:3]:
                    print(f"    - {repo.name} (relevance: {repo.relevance_score:.1%})")
            
            if result.job_match_result.recommendations:
                print(f"  • Recommendations:")
                for rec in result.job_match_result.recommendations[:3]:
                    print(f"    - {rec}")
        
        print("\n" + "=" * 50)
        print("✅ Analysis completed successfully!")
        print("📁 Results saved to 'output/' directory")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()