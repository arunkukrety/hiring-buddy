"""Enhanced Candidate Evaluation System - Intelligent Job-Candidate Matching

This script implements the complete workflow you described:
1. Planner Agent orchestrates everything
2. Resume Parser Agent extracts info (including GitHub links)
3. GitHub Agent does initial scan
4. Planner Agent matches against job description
5. Planner Agent identifies relevant repositories
6. GitHub Agent does deep code analysis of specific repos
7. Planner Agent analyzes code quality and provides final assessment
"""

import sys
from pathlib import Path

from portia import Portia, Config
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput
from portia.cli import CLIExecutionHooks

from agents.enhanced_planner_agent import EnhancedPlannerAgent


def main():
    """Main function for enhanced candidate evaluation."""
    
    print("🚀 Enhanced Candidate Evaluation System")
    print("🤖 Intelligent Job-Candidate Matching Workflow")
    print("=" * 60)
    
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
            execution_hooks=CLIExecutionHooks(),
        )
        
        # create enhanced planner agent
        print("🤖 Creating enhanced planner agent...")
        planner = EnhancedPlannerAgent(portia)
        
        # perform intelligent job-candidate matching
        print("🎯 Starting intelligent job-candidate matching workflow...")
        result = planner.analyze_candidate_for_job(resume_path, job_description_path)
        
        # display comprehensive results
        print("\n" + "=" * 60)
        print("ENHANCED CANDIDATE EVALUATION RESULTS")
        print("=" * 60)
        
        # display candidate and job info
        print(f"\n🎯 CANDIDATE: {result.candidate_info['candidate_name']}")
        print(f"📋 POSITION: {result.job_description.title}")
        print(f"🏢 COMPANY: {result.job_description.company or 'Not specified'}")
        print(f"📍 LOCATION: {result.job_description.location or 'Not specified'}")
        
        # display match score
        print(f"\n📊 OVERALL MATCH SCORE: {result.match_score:.1%}")
        
        # display skill matches
        if result.skill_matches:
            print(f"\n🔍 SKILL MATCHING ANALYSIS:")
            required_matches = [m for m in result.skill_matches if m["required"]]
            preferred_matches = [m for m in result.skill_matches if not m["required"]]
            
            if required_matches:
                print(f"  📋 REQUIRED SKILLS ({len(required_matches)}):")
                for match in required_matches:
                    status = "✅" if match["candidate_has"] else "❌"
                    print(f"    {status} {match['skill']}")
            
            if preferred_matches:
                print(f"  💡 PREFERRED SKILLS ({len(preferred_matches)}):")
                for match in preferred_matches:
                    status = "✅" if match["candidate_has"] else "❌"
                    print(f"    {status} {match['skill']}")
        
        # display github analysis
        if result.github_analysis:
            print(f"\n🐙 GITHUB PROFILE ANALYSIS:")
            github = result.github_analysis
            print(f"  • Username: {github.username}")
            print(f"  • Public Repos: {github.public_repos}")
            print(f"  • Followers: {github.followers}")
            print(f"  • Following: {github.following}")
            
            if github.contributions:
                print(f"  • Total Contributions: {github.contributions.total_contributions}")
                print(f"  • Total Commits: {github.contributions.total_commits}")
                print(f"  • Active Days: {github.contributions.active_days}")
        
        # display relevant repositories
        if result.relevant_repositories:
            print(f"\n🔍 RELEVANT REPOSITORIES ({len(result.relevant_repositories)} found):")
            for i, repo in enumerate(result.relevant_repositories, 1):
                print(f"  {i}. 📁 {repo.name} (Relevance: {repo.relevance_score:.1f})")
                print(f"     • Languages: {', '.join(repo.languages_used[:3])}")
                print(f"     • Frameworks: {', '.join(repo.frameworks_detected[:3])}")
                print(f"     • Complexity: {repo.project_complexity}")
                if repo.code_quality_indicators:
                    print(f"     • Quality: {', '.join(repo.code_quality_indicators[:2])}")
        
        # display code analysis
        if result.code_analysis:
            print(f"\n💻 DEEP CODE ANALYSIS:")
            code_analysis = result.code_analysis
            
            if code_analysis.get("languages_found"):
                print(f"  • Languages Found: {', '.join(code_analysis['languages_found'])}")
            
            if code_analysis.get("frameworks_detected"):
                print(f"  • Frameworks Detected: {', '.join(code_analysis['frameworks_detected'])}")
            
            if code_analysis.get("coding_patterns"):
                print(f"  • Coding Patterns: {', '.join(code_analysis['coding_patterns'])}")
            
            if code_analysis.get("code_quality_indicators"):
                print(f"  • Quality Indicators: {', '.join(code_analysis['code_quality_indicators'])}")
        
        # display overall assessment
        print(f"\n📋 OVERALL ASSESSMENT:")
        print(f"  {result.overall_assessment}")
        
        # display recommendations
        if result.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"  {i}. {rec}")
        
        # display detailed analysis summary
        print(f"\n📊 DETAILED ANALYSIS SUMMARY:")
        
        # calculate skill match percentage
        if result.skill_matches:
            required_skills = [m for m in result.skill_matches if m["required"]]
            preferred_skills = [m for m in result.skill_matches if not m["required"]]
            
            required_match_rate = len([m for m in required_skills if m["candidate_has"]]) / len(required_skills) if required_skills else 0
            preferred_match_rate = len([m for m in preferred_skills if m["candidate_has"]]) / len(preferred_skills) if preferred_skills else 0
            
            print(f"  • Required Skills Match: {required_match_rate:.1%}")
            print(f"  • Preferred Skills Match: {preferred_match_rate:.1%}")
        
        # github activity assessment
        if result.github_analysis and result.github_analysis.contributions:
            total_contributions = result.github_analysis.contributions.total_contributions
            if total_contributions > 1000:
                activity_level = "Very High"
            elif total_contributions > 500:
                activity_level = "High"
            elif total_contributions > 100:
                activity_level = "Moderate"
            else:
                activity_level = "Low"
            
            print(f"  • GitHub Activity Level: {activity_level}")
        
        # repository quality assessment
        if result.relevant_repositories:
            high_quality_repos = [repo for repo in result.relevant_repositories if repo.relevance_score > 0.7]
            print(f"  • High-Quality Relevant Repos: {len(high_quality_repos)}/{len(result.relevant_repositories)}")
        
        print("\n" + "=" * 60)
        print("✅ Enhanced evaluation completed successfully!")
        print("🤖 This system provides intelligent, job-focused candidate assessment")
        print("📊 Results saved to output/ directory")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def create_sample_job_description():
    """Create a sample job description for testing."""
    
    sample_job = """Job Title: Frontend Engineer (Fresher)

Location: Remote / Work from Home

Job Type: Full-Time

About Us:
We are a fast-growing tech startup focused on building innovative web applications for users worldwide. We value creativity, collaboration, and a strong passion for learning.

Job Description:
We are looking for a motivated and enthusiastic Frontend Engineer (Fresher) to join our team. You will work closely with our design and backend teams to create responsive, user-friendly web applications. This is an excellent opportunity for fresh graduates who want to kickstart their career in frontend development.

Key Responsibilities:

Develop responsive web applications using HTML, CSS, and JavaScript.

Collaborate with UI/UX designers to implement high-quality designs.

Ensure cross-browser and cross-device compatibility.

Optimize web applications for maximum speed and scalability.

Write clean, maintainable, and well-documented code.

Work closely with backend developers to integrate APIs.

Participate in code reviews and contribute to improving development processes.

Required Skills:

Proficiency in HTML5, CSS3, and JavaScript (ES6+).

Familiarity with frontend frameworks/libraries such as React, Angular, or Vue.js.

Knowledge of responsive design, Bootstrap, Tailwind CSS, or Material UI.

Basic understanding of REST APIs and integrating frontend with backend.

Familiarity with version control systems (e.g., Git, GitHub).

Problem-solving skills and attention to detail.

Good communication and teamwork abilities.

Preferred Skills (Optional):

Knowledge of TypeScript.

Experience with state management libraries like Redux or Context API.

Familiarity with frontend testing frameworks (e.g., Jest, Cypress).

Understanding of web performance optimization techniques.

Educational Qualification:

Bachelor's degree in Computer Science, Information Technology, or related fields.

Experience:

Freshers are welcome. Internships or personal projects will be considered a plus.

Perks and Benefits:

Flexible working hours and remote work options.

Opportunity to work on real-world projects and modern tech stacks.

Mentorship from experienced engineers.

Friendly and collaborative work environment.

How to Apply:

Submit your resume and GitHub/portfolio links.

Include any personal projects or contributions that demonstrate your frontend skills.
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
