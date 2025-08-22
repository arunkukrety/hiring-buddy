import os
from pathlib import Path
from dotenv import load_dotenv
from portia import Config, Portia, DefaultToolRegistry
from portia.cli import CLIExecutionHooks

from agents.planner_agent import PlannerAgent

load_dotenv(override=True)

# Check if we have the required API key
if not os.getenv('OPENAI_API_KEY') and not os.getenv('GOOGLE_API_KEY'):
    raise ValueError("Please set either OPENAI_API_KEY or GOOGLE_API_KEY in your .env file")

print("Creating Portia configuration...")

# Use the default config which will automatically detect available API keys
config = Config.from_default()

print("Creating Portia instance...")

# Create Portia instance with default tools and CLI execution hooks
portia = Portia(
    config=config,
    tools=DefaultToolRegistry(config=config),
    execution_hooks=CLIExecutionHooks(),
)

print("Portia instance created successfully")

# Resume source - specified in main.py as requested
RESUME_SOURCE = "resume.pdf"

def main():
    """Main function to run the dynamic resume analysis workflow"""
    print(f"Starting dynamic resume analysis for: {RESUME_SOURCE}")
    
    # Check if resume file exists
    resume_path = Path(RESUME_SOURCE)
    if not resume_path.exists():
        print(f"Error: Resume file '{RESUME_SOURCE}' not found!")
        return
    
    try:
        # Create planner agent
        print("Creating planner agent...")
        planner_agent = PlannerAgent(portia)
        
        # Analyze the resume using the planning system
        print("Analyzing resume with dynamic LLM-based parsing...")
        analysis_result = planner_agent.analyze_resume(str(resume_path))
        
        # Display results
        print("\n" + "="*60)
        print("DYNAMIC RESUME ANALYSIS RESULTS")
        print("="*60)
        
        # Candidate Information
        candidate_info = analysis_result.candidate_info
        print(f"\n📋 Candidate: {candidate_info.get('name', 'Not found')}")
        print(f"📧 Email: {candidate_info.get('email', 'Not found')}")
        print(f"📱 Phone: {candidate_info.get('phone', 'Not found')}")
        
        if candidate_info.get('linkedin'):
            print(f"💼 LinkedIn: {candidate_info['linkedin']}")
        if candidate_info.get('github'):
            print(f"🐙 GitHub: {candidate_info['github']}")
        if candidate_info.get('portfolio'):
            print(f"🌐 Portfolio: {candidate_info['portfolio']}")
        
        # Analysis Summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"  • {analysis_result.education_summary}")
        print(f"  • {analysis_result.skills_summary}")
        print(f"  • {analysis_result.projects_summary}")
        
        # Overall Assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"  {analysis_result.overall_assessment}")
        
        # Recommendations
        if analysis_result.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(analysis_result.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)
        print("Dynamic analysis completed successfully!")
        print("🔧 This system can handle ANY resume format using LLM!")
        
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()