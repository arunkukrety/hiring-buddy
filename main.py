"""Main entry point and web workflow for GitHub Portia system.

This file previously became corrupted by overlapping edits. It has been
cleaned and simplified. The CLI main() remains minimal; the enhanced
main_workflow() is used by the web UI and streams granular steps.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from portia import Portia, Config, LLMProvider, PortiaToolRegistry, LogLevel
from agents import PlannerAgent, SchedulerAgent
from tools.candidate_tracker import CandidateTracker
from utils.cli import create_sample_job_description


def main():
    """CLI execution (kept lean)."""
    load_dotenv()
    required = ["GOOGLE_API_KEY", "PORTIA_API_KEY"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        sys.exit(1)

    config = Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        portia_api_key=os.getenv("PORTIA_API_KEY"),
        default_log_level=LogLevel.ERROR  # Suppress INFO messages
    )
    portia = Portia(config, tools=PortiaToolRegistry(config))

    resume = Path("resume.pdf")
    if not resume.exists():
        print("resume.pdf not found")
        sys.exit(1)
    job_file = Path("job_description.txt")
    if not job_file.exists():
        create_sample_job_description()

    planner = PlannerAgent(portia)
    result = planner.analyze_resume(str(resume), str(job_file))
    print("Analysis complete (CLI mode). Use web UI for detailed streaming.")
    return result


def main_workflow(resume_path: str, job_description_path: str):
    """Web UI workflow: streams step-by-step analysis, scoring & email preview."""

    class _WebStream:
        def write(self, text):
            if text.strip():
                try:
                    from app import global_add_output
                    global_add_output(text.rstrip())
                except Exception:
                    sys.__stdout__.write(text)
        def flush(self):
            pass

    # Attach streaming unless already wrapped
    if sys.stdout.__class__.__name__ not in {"_WebStream", "WebOutput"}:
        sys.stdout = _WebStream()

    def step(idx, total, title):
        print(f"{title}")

    TOTAL = 8
    try:
        load_dotenv()
        # If env keys are present use configured models, else fall back to default ctor
        if os.getenv("GOOGLE_API_KEY") and os.getenv("PORTIA_API_KEY"):
            try:
                config = Config.from_default(
                    llm_provider=LLMProvider.GOOGLE,
                    default_model="google/gemini-1.5-flash",  # Use the standard model instead of 2.0
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    portia_api_key=os.getenv("PORTIA_API_KEY"),
                    default_log_level=LogLevel.ERROR  # Suppress INFO messages
                )
                portia = Portia(config, tools=PortiaToolRegistry(config))
            except Exception as api_error:
                print(f"<div style='background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444;'>")
                print(f"<h3><strong>⚠️ API Configuration Issue</strong></h3>")
                print(f"<p>Google API quota exceeded or configuration error. Falling back to basic analysis.</p>")
                print(f"<p><strong>Error:</strong> {str(api_error)}</p>")
                print(f"</div>")
                # Fallback to basic config
                config = Config.from_default(default_log_level=LogLevel.ERROR)
                portia = Portia(config)
        else:
            # Create config with minimal logging for default case
            config = Config.from_default(default_log_level=LogLevel.ERROR)
            portia = Portia(config)

        planner = PlannerAgent(portia)
        tracker = CandidateTracker()

        
       
        

        step(1, TOTAL, "<h2><strong>🔄 Running End-to-End Analysis</strong></h2><p>Analyzing resume + GitHub profile + job matching...</p>")
        
        try:
            result = planner.analyze_resume(resume_path, job_description_path)
        except Exception as analysis_error:
            # Handle API quota exceeded or other analysis errors
            error_output = []
            error_output.append("<div style='background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444;'>")
            error_output.append("<h3><strong>⚠️ Analysis Error Encountered</strong></h3>")
            
            if "quota" in str(analysis_error).lower() or "429" in str(analysis_error):
                error_output.append("<p><strong>Google API Quota Exceeded:</strong> You've reached the daily limit of 200 requests for the free tier.</p>")
                error_output.append("<p><strong>Solutions:</strong></p>")
                error_output.append("<ul>")
                error_output.append("<li>Wait 24 hours for quota reset</li>")
                error_output.append("<li>Upgrade to paid Google AI API plan</li>")
                error_output.append("<li>Use OpenAI API as alternative (add OPENAI_API_KEY to .env)</li>")
                error_output.append("</ul>")
            else:
                error_output.append(f"<p><strong>Error:</strong> {str(analysis_error)}</p>")
            
            error_output.append("</div>")
            step(1.5, TOTAL, '\n'.join(error_output))
            return None
        
        candidate_name = result.candidate_info.get('candidate_name', 'Unknown')
        job_title = result.job_match_result.job_description.title if result.job_match_result else 'Position'
        match_score = result.job_match_result.match_score if result.job_match_result else 0.0

        # If job matching failed but we have GitHub analysis, still show it
        if not result.job_match_result and result.github_analysis:
            fallback_output = []
            fallback_output.append("<div style='background-color: #fffbeb; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;'>")
            fallback_output.append("<h3><strong>⚠️ Limited Analysis Mode</strong></h3>")
            fallback_output.append("<p>Job matching failed due to API limitations, but GitHub analysis is available.</p>")
            fallback_output.append("</div>")
            print('\n'.join(fallback_output))

        # Group candidate profile information together
        profile_output = []
        profile_output.append("<h2><strong>👤 Candidate Profile & GitHub Summary</strong></h2>")
        profile_output.append("<div style='background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
        profile_output.append(f"<h3><strong>Basic Information</strong></h3>")
        profile_output.append("<ul>")
        profile_output.append(f"<li><strong>Candidate:</strong> {candidate_name}</li>")
        profile_output.append(f"<li><strong>Position:</strong> {job_title}</li>")
        profile_output.append(f"<li><strong>Overall Match Score:</strong> <span style='color: #007acc; font-weight: bold;'>{match_score:.1%}</span></li>")
        profile_output.append("</ul>")
        
        if result.github_analysis:
            gh = result.github_analysis
            profile_output.append(f"<h3><strong>GitHub Activity Summary</strong></h3>")
            profile_output.append("<ul>")
            profile_output.append(f"<li><strong>Public Repositories:</strong> {gh.public_repos}</li>")
            if gh.contributions:
                profile_output.append(f"<li><strong>Total Commits:</strong> {gh.contributions.total_commits}</li>")
                profile_output.append(f"<li><strong>Total Contributions:</strong> {gh.contributions.total_contributions}</li>")
                profile_output.append(f"<li><strong>Pull Requests:</strong> {gh.contributions.total_prs}</li>")
                profile_output.append(f"<li><strong>Code Reviews:</strong> {gh.contributions.total_reviews}</li>")
                profile_output.append(f"<li><strong>Active Days:</strong> {gh.contributions.active_days}</li>")
            profile_output.append("</ul>")
        else:
            profile_output.append("<p><em>No GitHub analysis available</em></p>")
        
        profile_output.append("</div>")
        step(2, TOTAL, '\n'.join(profile_output))

        # Add detailed GitHub analysis step
        if result.github_analysis:
            github_output = []
            github_output.append("<h2><strong>🐙 Detailed GitHub Profile Analysis</strong></h2>")
            
            gh = result.github_analysis
            
            # Profile Information
            github_output.append("<div style='background-color: #f6f8fa; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
            github_output.append("<h3><strong>📊 Profile Overview</strong></h3>")
            github_output.append("<ul>")
            github_output.append(f"<li><strong>Username:</strong> {gh.username}</li>")
            if gh.name:
                github_output.append(f"<li><strong>Name:</strong> {gh.name}</li>")
            if gh.bio:
                github_output.append(f"<li><strong>Bio:</strong> {gh.bio}</li>")
            if gh.company:
                github_output.append(f"<li><strong>Company:</strong> {gh.company}</li>")
            if gh.location:
                github_output.append(f"<li><strong>Location:</strong> {gh.location}</li>")
            github_output.append(f"<li><strong>Public Repositories:</strong> {gh.public_repos}</li>")
            github_output.append("</ul>")
            github_output.append("</div>")
            
            # Contribution Analysis
            if gh.contributions:
                contrib = gh.contributions
                github_output.append("<div style='background-color: #e6fffa; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
                github_output.append("<h3><strong>💻 Contribution Activity</strong></h3>")
                github_output.append("<ul>")
                github_output.append(f"<li><strong>Total Contributions:</strong> {contrib.total_contributions}</li>")
                github_output.append(f"<li><strong>Total Commits:</strong> {contrib.total_commits}</li>")
                github_output.append(f"<li><strong>Pull Requests:</strong> {contrib.total_prs}</li>")
                github_output.append(f"<li><strong>Code Reviews:</strong> {contrib.total_reviews}</li>")
                github_output.append(f"<li><strong>Active Days:</strong> {contrib.active_days}</li>")
                github_output.append("</ul>")
                github_output.append("</div>")
            
            # Repository Analysis
            if gh.repositories:
                github_output.append("<div style='background-color: #fff5b4; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
                github_output.append(f"<h3><strong>📁 Repository Analysis ({len(gh.repositories)} repositories)</strong></h3>")
                
                # Show top repositories by relevance/activity
                sorted_repos = sorted(gh.repositories, key=lambda r: r.relevance_score if hasattr(r, 'relevance_score') else 0, reverse=True)[:5]
                
                github_output.append("<ul>")
                for i, repo in enumerate(sorted_repos, 1):
                    github_output.append(f"<li><strong>{repo.name}</strong>")
                    if hasattr(repo, 'description') and repo.description:
                        github_output.append(f" - {repo.description}")
                    github_output.append("<ul>")
                    if hasattr(repo, 'languages') and repo.languages:
                        # repo.languages is a list, take first 3
                        top_langs = repo.languages[:3]
                        github_output.append(f"<li>Languages: {', '.join(top_langs)}</li>")
                    if hasattr(repo, 'stars') and repo.stars:
                        github_output.append(f"<li>Stars: {repo.stars}</li>")
                    if hasattr(repo, 'forks') and repo.forks:
                        github_output.append(f"<li>Forks: {repo.forks}</li>")
                    github_output.append("</ul></li>")
                github_output.append("</ul>")
                github_output.append("</div>")
            
            # Language Analysis
            all_languages = set()
            if gh.repositories:
                for repo in gh.repositories:
                    if hasattr(repo, 'languages') and repo.languages:
                        # repo.languages is a list, not a dict
                        all_languages.update(repo.languages)
                
                if all_languages:
                    # Convert set to list and take first 10
                    lang_list = list(all_languages)[:10]
                    github_output.append("<div style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
                    github_output.append("<h3><strong>💻 Programming Languages Used</strong></h3>")
                    github_output.append("<ul>")
                    for lang in lang_list:
                        github_output.append(f"<li>{lang}</li>")
                    github_output.append("</ul>")
                    github_output.append("</div>")
            
            # Profile Summary
            if hasattr(gh, 'profile_summary') and gh.profile_summary:
                github_output.append("<div style='background-color: #fef3c7; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
                github_output.append("<h3><strong>📝 AI-Generated Profile Summary</strong></h3>")
                github_output.append(f"<p>{gh.profile_summary}</p>")
                github_output.append("</div>")
            
            step(2.5, TOTAL, '\n'.join(github_output))

        step(3, TOTAL, "<h2><strong>📊 Performance Evaluation & Scoring</strong></h2>")
        breakdown = getattr(result.job_match_result, 'score_breakdown', {}) if result.job_match_result else {}
        if isinstance(breakdown, dict) and breakdown:
            # Build complete evaluation output as single string with HTML formatting
            evaluation_output = []
            evaluation_output.append(f"<h1><strong>PERFORMANCE EVALUATION SUMMARY</strong></h1>")
            evaluation_output.append(f"")
            evaluation_output.append(f"<h2><strong>Overall Assessment</strong></h2>")
            evaluation_output.append(f"<ul>")
            evaluation_output.append(f"<li><strong>Match Score:</strong> {match_score:.1%} for <strong>{job_title}</strong></li>")
            evaluation_output.append(f"<li><strong>Assessment:</strong> {result.job_match_result.overall_assessment if result.job_match_result else 'N/A'}</li>")
            evaluation_output.append(f"</ul>")
            evaluation_output.append(f"")
            
            # Component scores with full analysis
            evaluation_output.append(f"<h2><strong>DETAILED COMPONENT SCORES</strong></h2>")
            evaluation_output.append(f"")
            for comp, details in breakdown.items():
                if isinstance(details, dict) and 'score' in details and comp not in {'detected_skills','scoring_criteria','strengths','weaknesses','recommendations','final_recommendation'}:
                    v = details['score']
                    disp = f"{v:.1f}%" if v > 1 else f"{v*100:.1f}%"
                    reason = details.get('reasoning', '')  # Full reasoning, no truncation
                    evaluation_output.append(f"<h3><strong>{comp.replace('_',' ').title()}:</strong> <span style='color: #007acc;'>{disp}</span></h3>")
                    evaluation_output.append(f"<p>{reason}</p>")
                    evaluation_output.append(f"")
            
            # Key insights (full analysis)
            for key,label in [('strengths','<h2><strong>Key Strengths</strong></h2>'),('weaknesses','<h2><strong>Areas for Improvement</strong></h2>'),('recommendations','<h2><strong>Recommendations</strong></h2>')]:
                items = breakdown.get(key)
                if items:
                    evaluation_output.append(f"{label}")
                    evaluation_output.append(f"<ul>")
                    for it in items:  # Show all items, not just top 3
                        evaluation_output.append(f"<li>{it}</li>")
                    evaluation_output.append(f"</ul>")
                    evaluation_output.append(f"")
            
            if breakdown.get('final_recommendation'):
                evaluation_output.append(f"<h2><strong>Final AI Recommendation</strong></h2>")
                evaluation_output.append(f"<div style='background-color: #f0f8ff; padding: 15px; border-left: 4px solid #007acc; margin: 10px 0;'>")
                evaluation_output.append(f"<p>{breakdown['final_recommendation']}</p>")
                evaluation_output.append(f"</div>")
                evaluation_output.append(f"")
                
            # Skills summary (full analysis)
            ds = breakdown.get('detected_skills')
            if ds:
                evaluation_output.append(f"<h2><strong>Detected Skills Summary</strong></h2>")
                evaluation_output.append(f"<ul>")
                skill_categories = ['programming_languages','frameworks','databases','tools']
                for k in skill_categories:
                    if ds.get(k):
                        evaluation_output.append(f"<li><strong>{k.replace('_',' ').title()}:</strong> {', '.join(ds[k])}</li>")  # Show all skills, not just top 3
                evaluation_output.append(f"</ul>")
                evaluation_output.append(f"")
            
            print('\n'.join(evaluation_output))
        else:
            print("<p><em>No detailed scoring breakdown available</em></p>")

        # Human decision with styled prompt
        decision_prompt = []
        decision_prompt.append("<h2><strong>🤔 Decision Point</strong></h2>")
        decision_prompt.append("<div style='background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;'>")
        decision_prompt.append("<p><strong>Please review the analysis above and make a decision:</strong></p>")
        decision_prompt.append("<p>• <strong>YES:</strong> Proceed with email generation and interview scheduling</p>")
        decision_prompt.append("<p>• <strong>NO:</strong> Reject candidate and move to next</p>")
        decision_prompt.append("</div>")
        step(5, TOTAL, '\n'.join(decision_prompt))
        
        while True:
            decision = input("Proceed with candidate? (yes/no): ").strip().lower()
            if decision in {'yes','y','no','n'}:
                break
            print("Please answer yes or no.")

        scheduler = None
        if decision in {'yes','y'}:
            step(6, TOTAL, "<h2><strong>✉️ Email Template Generation & Preview</strong></h2>")
            scheduler = SchedulerAgent(portia)
            emails = scheduler.generate_email_templates(result.candidate_info, result.job_match_result.job_description, match_score)
            
            # Group both email previews in a single formatted message
            email_previews = []
            email_previews.append("<h2><strong>📧 Email Templates Generated</strong></h2>")
            email_previews.append("")
            
            # Candidate email preview
            email_previews.append("<div style='background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #0ea5e9;'>")
            email_previews.append("<h3><strong>📨 Candidate Email Preview</strong></h3>")
            email_previews.append(f"<p><strong>To:</strong> {result.candidate_info.get('email', 'No email found')}</p>")
            email_previews.append(f"<p><strong>Subject:</strong> {emails['candidate']['subject']}</p>")
            email_previews.append("<hr style='margin: 10px 0; border: 1px solid #e0e7ff;'>")
            email_previews.append(f"<div style='white-space: pre-line; font-family: system-ui;'>{emails['candidate']['body']}</div>")
            email_previews.append("</div>")
            email_previews.append("")
            
            # Manager email preview
            email_previews.append("<div style='background-color: #f0fdf4; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #22c55e;'>")
            email_previews.append("<h3><strong>👔 Manager Email Preview</strong></h3>")
            email_previews.append(f"<p><strong>To:</strong> Hiring Manager</p>")
            email_previews.append(f"<p><strong>Subject:</strong> {emails['manager']['subject']}</p>")
            email_previews.append("<hr style='margin: 10px 0; border: 1px solid #dcfce7;'>")
            email_previews.append(f"<div style='white-space: pre-line; font-family: system-ui;'>{emails['manager']['body']}</div>")
            email_previews.append("</div>")
            
            print('\n'.join(email_previews))
            
            cust = input("\nEmail customization instructions (Enter to keep as-is): ").strip()
            if cust:
                customization_output = []
                customization_output.append("<h3><strong>🔧 Customizing Emails...</strong></h3>")
                customization_output.append(f"<p><em>Applying customization: {cust}</em></p>")
                print('\n'.join(customization_output))
                
                emails = scheduler.customize_existing_emails(emails, cust, result.candidate_info, result.job_match_result.job_description, match_score)
                
                updated_email = []
                updated_email.append("<h3><strong>📧 Updated Candidate Email</strong></h3>")
                updated_email.append("<div style='background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;'>")
                updated_email.append(f"<div style='white-space: pre-line; font-family: system-ui;'>{emails['candidate']['body']}</div>")
                updated_email.append("</div>")
                print('\n'.join(updated_email))
                
            send = input("\nSend emails & schedule interview? (yes/no): ").strip().lower()
            if send in {'yes','y'}:
                step(7, TOTAL, "<h2><strong>📅 Scheduling Interview & Sending Notifications</strong></h2>")
                sched_res = scheduler.schedule_interview_and_notify(result.candidate_info, result.job_match_result.job_description, match_score, email_templates=emails)
                
                scheduling_result = []
                if sched_res.get('success'):
                    scheduling_result.append("<div style='background-color: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 4px solid #22c55e;'>")
                    scheduling_result.append("<h3><strong>✅ Interview Successfully Scheduled</strong></h3>")
                    scheduling_result.append(f"<p><strong>Date:</strong> {sched_res.get('interview_date')}</p>")
                    scheduling_result.append("<p><strong>Status:</strong> Emails sent, calendar invites created</p>")
                    scheduling_result.append("</div>")
                    CandidateTracker().log_decision(candidate_name, 'yes', interview_date=sched_res.get('interview_date'), notes=f"Scheduled. Match {match_score:.1%}")
                else:
                    scheduling_result.append("<div style='background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444;'>")
                    scheduling_result.append("<h3><strong>❌ Scheduling Issues Encountered</strong></h3>")
                    scheduling_result.append("<p>Please check the logs for more details</p>")
                    scheduling_result.append("</div>")
                print('\n'.join(scheduling_result))
            else:
                cancelled_output = []
                cancelled_output.append("<div style='background-color: #f3f4f6; padding: 15px; border-radius: 8px; border-left: 4px solid #6b7280;'>")
                cancelled_output.append("<h3><strong>⏸️ Scheduling Cancelled</strong></h3>")
                cancelled_output.append("<p>User chose not to proceed after email preview</p>")
                cancelled_output.append("</div>")
                print('\n'.join(cancelled_output))
                CandidateTracker().log_decision(candidate_name,'no',notes=f"Cancelled post-preview. Match {match_score:.1%}")
        else:
            rejection_output = []
            rejection_output.append("<div style='background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444;'>")
            rejection_output.append("<h3><strong>❌ Candidate Rejected</strong></h3>")
            rejection_output.append("<p>User decided not to proceed before email generation</p>")
            rejection_output.append("</div>")
            print('\n'.join(rejection_output))
            CandidateTracker().log_decision(candidate_name,'no',notes=f"Rejected. Match {match_score:.1%}")

        # Final tracking summary with enhanced formatting
        tracking_output = []
        tracking_output.append("<h2><strong>📊 Workflow Summary & Tracking</strong></h2>")
        tracking_output.append("<div style='background-color: #f8fafc; padding: 15px; border-radius: 8px; margin: 10px 0;'>")
        
        tracker_summary = CandidateTracker().get_tracking_summary()
        tracking_output.append("<h3><strong>Candidate Processing Summary</strong></h3>")
        tracking_output.append("<ul>")
        for status,count in tracker_summary['status_counts'].items():
            tracking_output.append(f"<li><strong>{status.title()}:</strong> {count} candidates</li>")
        tracking_output.append("</ul>")
        tracking_output.append("<p><em>Data exported for Google Sheets integration</em></p>")
        tracking_output.append("</div>")
        tracking_output.append("<h3><strong>🎉 Workflow Complete!</strong></h3>")
        
        step(8, TOTAL, '\n'.join(tracking_output))
        CandidateTracker().export_for_google_sheets()
        return result
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()