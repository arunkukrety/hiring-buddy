"""Main entry point for the GitHub Portia system."""

import os
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

from portia import Portia, Config, LLMProvider, PlanRunState, ValueConfirmationClarification, PortiaToolRegistry
from portia.cli import CLIExecutionHooks

from agents import PlannerAgent, SchedulerAgent
from tools.candidate_tracker import CandidateTracker
from utils.cli import create_sample_job_description


def main():
    """Main function to run the GitHub Portia system."""
    
    # load environment variables
    load_dotenv()
    
    # check required environment variables
    required_vars = ["GOOGLE_API_KEY", "PORTIA_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        print("\n📋 Required setup:")
        print("1. GOOGLE_API_KEY - For Gemini LLM (you already have this)")
        print("2. PORTIA_API_KEY - For email/calendar features (get from https://app.portialabs.ai/)")
        sys.exit(1)
    
    # initialize portia with Gemini configuration and Portia Cloud tools
    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        portia_api_key=os.getenv("PORTIA_API_KEY")
    )
    portia = Portia(config, tools=PortiaToolRegistry(config))
    
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
        # initialize candidate tracker
        tracker = CandidateTracker()
        
        # create planner agent
        planner = PlannerAgent(portia)
        
        # perform complete analysis
        print("🤖 Starting complete analysis workflow...")
        result = planner.analyze_resume(str(resume_path), str(job_description_path))
        
        # log resume received
        tracker.log_resume_received(
            result.candidate_info,
            str(resume_path),
            result.job_match_result.job_description
        )
        

        
        # update tracking with analysis results
        tracker.update_analysis_results(
            candidate_name=result.candidate_info.get('candidate_name', 'Unknown'),
            analysis_results=result.job_match_result.score_breakdown,
            analysis_file=f"output/enhanced_analysis_{result.candidate_info.get('candidate_name', 'Unknown').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        

        
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
        
        # skills summary - use AI-detected skills if available
        if hasattr(result, 'job_match_result') and result.job_match_result and hasattr(result.job_match_result, 'score_breakdown'):
            breakdown = result.job_match_result.score_breakdown
            if isinstance(breakdown, dict) and 'detected_skills' in breakdown:
                skills_data = breakdown['detected_skills']
                total_skills = skills_data.get('skill_count', 0)
                print(f"\n🛠️ AI-Detected Skills ({total_skills} total):")
                
                if skills_data.get('programming_languages'):
                    print(f"  • Programming Languages: {', '.join(skills_data['programming_languages'][:5])}")
                if skills_data.get('frameworks'):
                    print(f"  • Frameworks: {', '.join(skills_data['frameworks'][:5])}")
                if skills_data.get('databases'):
                    print(f"  • Databases: {', '.join(skills_data['databases'][:5])}")
                if skills_data.get('cloud_platforms'):
                    print(f"  • Cloud Platforms: {', '.join(skills_data['cloud_platforms'][:5])}")
                if skills_data.get('tools'):
                    print(f"  • Tools: {', '.join(skills_data['tools'][:5])}")
                if skills_data.get('methodologies'):
                    print(f"  • Methodologies: {', '.join(skills_data['methodologies'][:5])}")
            else:
                # fallback to basic skills
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
        else:
            # fallback to basic skills
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
            
            # display AI evaluation details if available
            if hasattr(result.job_match_result, 'score_breakdown') and result.job_match_result.score_breakdown:
                breakdown = result.job_match_result.score_breakdown
                if isinstance(breakdown, dict) and 'strengths' in breakdown:
                    print(f"\n💪 Key Strengths:")
                    for strength in breakdown.get('strengths', [])[:3]:
                        print(f"  • {strength}")
                    
                    print(f"\n⚠️ Areas for Improvement:")
                    for weakness in breakdown.get('weaknesses', [])[:3]:
                        print(f"  • {weakness}")
                    
                    print(f"\n🎯 Recommendations:")
                    for rec in breakdown.get('recommendations', [])[:3]:
                        print(f"  • {rec}")
                    
                    if 'final_recommendation' in breakdown:
                        print(f"\n📋 Final Recommendation:")
                        print(f"  {breakdown['final_recommendation']}")
            
            # display detailed score breakdown if available
            if hasattr(result.job_match_result, 'score_breakdown') and result.job_match_result.score_breakdown:
                print(f"\n📊 Detailed Score Breakdown:")
                breakdown = result.job_match_result.score_breakdown
                if isinstance(breakdown, dict):
                    for component, details in breakdown.items():
                        if isinstance(details, dict) and 'score' in details:
                            score_pct = details["score"]
                            reasoning = details.get("reasoning", "No reasoning provided")
                            print(f"  • {component.replace('_', ' ').title()}: {score_pct:.1f}%")
                            print(f"    {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}")
                else:
                    print(f"  • Score breakdown format: {type(breakdown)}")
                    print(f"  • Content: {breakdown}")
                
                # display scoring criteria for transparency
                if hasattr(result.job_match_result, 'score_breakdown') and result.job_match_result.score_breakdown:
                    scoring_criteria = result.job_match_result.score_breakdown.get('scoring_criteria')
                    if scoring_criteria:
                        print(f"\n📋 SCORING CRITERIA (HR Transparency):")
                        print("=" * 50)
                        print(f"Overview: {scoring_criteria.get('overview', 'N/A')}")
                        
                        components = scoring_criteria.get('scoring_components', {})
                        for component, criteria in components.items():
                            print(f"\n{component.replace('_', ' ').title()} ({criteria.get('weight', 'N/A')}):")
                            print(f"  Description: {criteria.get('description', 'N/A')}")
                            print(f"  Criteria: {', '.join(criteria.get('criteria', []))}")
                        
                        print(f"\nOverall Score Interpretation:")
                        interpretation = scoring_criteria.get('overall_score_interpretation', {})
                        for range_desc, meaning in interpretation.items():
                            print(f"  • {range_desc}: {meaning}")
                        
                        print(f"\nTransparency Notes:")
                        notes = scoring_criteria.get('transparency_notes', [])
                        for note in notes:
                            print(f"  • {note}")
            
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
        
        # human-in-the-loop decision point
        print("\n🤔 HUMAN DECISION REQUIRED")
        print("=" * 50)
        
        candidate_name = result.candidate_info.get('candidate_name', 'Candidate')
        match_score = result.job_match_result.match_score if result.job_match_result else 0.0
        job_title = result.job_match_result.job_description.title if result.job_match_result else "Position"
        
        print(f"📋 Candidate: {candidate_name}")
        print(f"🎯 Position: {job_title}")
        print(f"📊 Match Score: {match_score:.1%}")
        print(f"📝 Assessment: {result.job_match_result.overall_assessment if result.job_match_result else 'N/A'}")
        
        # ask for user decision
        while True:
            print(f"\n❓ Should we proceed with {candidate_name} for the {job_title} position?")
            print("   This will:")
            print("   • Send an acceptance email to the candidate")
            print("   • Send a notification to the hiring manager")
            print("   • Schedule an interview for 7 days from now")
            
            user_input = input("\nEnter 'yes' to proceed or 'no' to reject: ").strip().lower()
            
            if user_input in ['yes', 'y']:
                print(f"\n✅ Proceeding with {candidate_name}...")
                
                # email preview and customization phase
                print(f"\n📧 EMAIL PREVIEW & CUSTOMIZATION")
                print("=" * 50)
                
                # create scheduler agent to generate email templates (ONCE)
                scheduler = SchedulerAgent(portia)
                email_templates = scheduler.generate_email_templates(
                    result.candidate_info,
                    result.job_match_result.job_description,
                    match_score
                )
                
                # show email preview
                print("\n📤 EMAIL TO CANDIDATE:")
                print("-" * 30)
                print(f"Subject: {email_templates['candidate']['subject']}")
                print(f"To: {result.candidate_info.get('email', 'No email found')}")
                print(f"\nBody:\n{email_templates['candidate']['body']}")
                
                print("\n📤 EMAIL TO MANAGER:")
                print("-" * 30)
                print(f"Subject: {email_templates['manager']['subject']}")
                print(f"To: Hiring Manager (via OAuth)")
                print(f"\nBody:\n{email_templates['manager']['body']}")
                
                # ask for customization
                print(f"\n✏️ EMAIL CUSTOMIZATION")
                print("-" * 30)
                print("Enter your instructions for email customization, or press Enter to use these templates.")
                print("\nExamples:")
                print("- 'Make the tone more formal and professional'")
                print("- 'Add that we're excited about their GitHub projects'")
                print("- 'Mention that the interview will include a coding challenge'")
                print("- 'Schedule for next Friday instead of 7 days from now'")
                
                custom_instructions = input("\n✏️ Enter your email customization instructions (or press Enter for defaults): ").strip()
                
                if custom_instructions:
                    print(f"\n🔧 Customizing emails based on: '{custom_instructions}'")
                    
                    # customize existing emails efficiently (no re-generation)
                    email_templates = scheduler.customize_existing_emails(
                        email_templates,
                        custom_instructions,
                        result.candidate_info,
                        result.job_match_result.job_description,
                        match_score
                    )
                    
                    # show updated preview
                    print("\n📤 UPDATED EMAIL TO CANDIDATE:")
                    print("-" * 30)
                    print(f"Subject: {email_templates['candidate']['subject']}")
                    print(f"Body:\n{email_templates['candidate']['body']}")
                    
                    print("\n📤 UPDATED EMAIL TO MANAGER:")
                    print("-" * 30)
                    print(f"Subject: {email_templates['manager']['subject']}")
                    print(f"Body:\n{email_templates['manager']['body']}")
                
                # get final confirmation
                print(f"\n📋 FINAL CONFIRMATION")
                print("=" * 50)
                print(f"Candidate: {candidate_name}")
                print(f"Position: {job_title}")
                if custom_instructions:
                    print(f"Custom instructions: {custom_instructions}")
                
                final_confirm = input("\n✅ Send these emails and schedule interview? (yes/no): ").strip().lower()
                if final_confirm not in ['yes', 'y']:
                    print("❌ Email sending cancelled.")
                    break
                
                # schedule interview using existing scheduler (no re-creation)
                scheduling_result = scheduler.schedule_interview_and_notify(
                    result.candidate_info,
                    result.job_match_result.job_description,
                    match_score,
                    email_templates=email_templates
                )
                
                if scheduling_result["success"]:
                    print(f"\n🎉 SUCCESS! Interview scheduled for {scheduling_result['interview_date']}")
                    print("📧 Emails sent to candidate and hiring manager")
                    print("📅 Calendar event created")
                    
                    # log decision and interview details
                    tracker.log_decision(
                        candidate_name=candidate_name,
                        decision="yes",
                        interview_date=scheduling_result.get('interview_date', ''),
                        interview_time="10:00 AM",  # default time
                        google_meet_link=None,
                        notes=f"Interview scheduled successfully. Match score: {match_score:.1%}"
                    )
                    

                    
                    print("\n📁 Results saved to 'output/' directory")
                else:
                    print(f"\n⚠️ Scheduling completed with some issues:")
                    print(f"   Interview date: {scheduling_result['interview_date']}")
                    if 'error' in scheduling_result:
                        print(f"   Error: {scheduling_result['error']}")
                
                break
                
            elif user_input in ['no', 'n']:
                print(f"\n❌ Rejected {candidate_name} for the {job_title} position.")
                
                # log rejection decision
                tracker.log_decision(
                    candidate_name=candidate_name,
                    decision="no",
                    notes=f"Candidate rejected. Match score: {match_score:.1%}"
                )
                

                
                print("📁 Analysis results saved to 'output/' directory")
                break
                
            else:
                print("❌ Please enter 'yes' or 'no'")
        
        # display tracking summary
        print("\n" + "=" * 50)
        print("📊 CANDIDATE TRACKING SUMMARY")
        print("=" * 50)
        summary = tracker.get_tracking_summary()
        print(f"📈 Total Candidates: {summary['total_candidates']}")
        print(f"📅 Last Updated: {summary['last_updated']}")
        print("\n📋 Status Breakdown:")
        for status, count in summary['status_counts'].items():
            print(f"  • {status.title()}: {count}")
        
        print(f"\n📊 CSV file ready for Google Sheets import:")
        csv_path = tracker.export_for_google_sheets()
        

        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()