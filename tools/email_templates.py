"""Email templates for candidate selection workflow."""

from typing import Dict, Any


class EmailTemplates:
    """Email templates for different notification scenarios."""
    
    @staticmethod
    def candidate_acceptance_email(
        candidate_name: str,
        job_title: str,
        company_name: str,
        interview_date: str,
        interview_time: str,
        calendar_link: str,
        google_meet_link: str = None
    ) -> Dict[str, str]:
        """Generate candidate acceptance email."""
        
        subject = f"Congratulations! You've been shortlisted for {job_title} position at {company_name}"
        
        body = f"""
Dear {candidate_name},

Congratulations! We are excited to inform you that your application for the {job_title} position at {company_name} has been shortlisted for the next round of our hiring process.

INTERVIEW DETAILS:
- Date: {interview_date}
- Time: {interview_time}
- Duration: 1 hour
- Format: Video call

WHAT TO EXPECT:
- Technical discussion about your experience and skills
- Questions about your projects and contributions
- Opportunity to ask questions about the role and company

PREPARATION TIPS:
- Review the job description and your application
- Prepare to discuss your technical projects and GitHub contributions
- Have questions ready about the role and company culture
- Ensure your video conferencing setup is working properly

NEED TO RESCHEDULE?
If you need to reschedule the interview, please contact us as soon as possible. You can also use this calendar link to suggest alternative times: {calendar_link}

NEXT STEPS:
1. Confirm your attendance by replying to this email
2. Check your calendar for the interview invitation
3. Please arrive 5 minutes early to ensure a smooth start

We look forward to meeting you and learning more about your experience and how you can contribute to our team.

Best regards,
{company_name} Hiring Team

---
This is an automated message. Please reply to this email if you have any questions.
"""
        
        return {
            "subject": subject,
            "body": body.strip()
        }
    
    @staticmethod
    def manager_notification_email(
        candidate_name: str,
        job_title: str,
        match_score: str,
        interview_date: str,
        interview_time: str
    ) -> Dict[str, str]:
        """Generate manager notification email."""
        
        subject = f"New Candidate Selected for {job_title} - {candidate_name}"
        
        body = f"""
Hi Hiring Manager,

A new candidate has been selected for the {job_title} position through our AI-powered screening system.

CANDIDATE DETAILS:
- Name: {candidate_name}
- Position: {job_title}
- Match Score: {match_score}
- Interview Scheduled: {interview_date} at {interview_time}

WHAT HAPPENS NEXT:
1. Candidate has been notified via email
2. Interview has been scheduled in your calendar
3. Calendar invites sent to all participants

CANDIDATE SUMMARY:
The AI system has analyzed the candidate's resume, GitHub profile, and project portfolio. Based on the comprehensive assessment, this candidate shows strong alignment with our requirements.

INTERVIEW PREPARATION:
- Review the candidate's full analysis in the output directory
- Check their GitHub profile for recent activity and code quality
- Prepare technical questions based on their skill set
- Consider their match score and assessment details

CALENDAR EVENT:
The interview has been automatically scheduled in your Google Calendar. You can modify the event or add additional participants as needed.

NEED TO MAKE CHANGES?
- Reschedule: Modify the calendar event directly
- Add participants: Edit the calendar event
- Cancel: Contact the candidate directly or use the calendar event

Let me know if you need any additional information about the candidate or have questions about the interview process.

Best regards,
AI Hiring Assistant

---
This is an automated notification from the GitHub Portia hiring system.
"""
        
        return {
            "subject": subject,
            "body": body.strip()
        }
    
    @staticmethod
    def calendar_event_description(
        candidate_name: str,
        job_title: str,
        interview_date: str,
        interview_time: str,
        google_meet_link: str = None
    ) -> str:
        """Generate calendar event description."""
        
        return f"""
Interview for {job_title} Position

INTERVIEW DETAILS:
- Candidate: {candidate_name}
- Position: {job_title}
- Date: {interview_date}
- Time: {interview_time}
- Duration: 1 hour
- Format: Video call

PREPARATION NOTES:
- Review candidate's resume and GitHub profile
- Check their technical projects and contributions
- Prepare questions based on their skill set
- Have the job description ready for reference

TECHNICAL SETUP:
- Ensure video conferencing software is ready
- Test audio and video equipment
- Have screen sharing capability available
- Prepare any technical assessment materials

INTERVIEW STRUCTURE:
1. Introduction and company overview (5 minutes)
2. Technical discussion and project review (30 minutes)
3. Behavioral questions and culture fit (15 minutes)
4. Candidate questions (10 minutes)

NEXT STEPS:
- Prepare feedback form for post-interview evaluation
- Schedule follow-up if needed

---
This event was automatically created by the GitHub Portia hiring system.
"""
