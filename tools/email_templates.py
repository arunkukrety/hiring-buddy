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
        """Generate candidate acceptance email with improved formatting."""
        
        subject = f"Congratulations! You've been shortlisted for {job_title} position at {company_name}"
        
        body = f"""<p><strong>Dear {candidate_name},</strong></p>

<p><strong>Congratulations!</strong> We are excited to inform you that your application for the <strong>{job_title}</strong> position at <strong>{company_name}</strong> has been shortlisted for the next round of our hiring process.</p>

<h3><strong>INTERVIEW DETAILS:</strong></h3>
<ul>
<li><strong>Date:</strong> {interview_date}</li>
<li><strong>Time:</strong> {interview_time}</li>
<li><strong>Duration:</strong> 1 hour</li>
<li><strong>Format:</strong> Video call</li>
</ul>

<h3><strong>WHAT TO EXPECT:</strong></h3>
<ul>
<li>Technical discussion about your experience and skills</li>
<li>Questions about your projects and contributions</li>
<li>Opportunity to ask questions about the role and company</li>
</ul>

<h3><strong>PREPARATION TIPS:</strong></h3>
<ul>
<li>Review the job description and your application</li>
<li>Prepare to discuss your technical projects and GitHub contributions</li>
<li>Have questions ready about the role and company culture</li>
<li>Ensure your video conferencing setup is working properly</li>
</ul>

<h3><strong>NEED TO RESCHEDULE?</strong></h3>
<p>If you need to reschedule the interview, please contact us as soon as possible.</p>

<h3><strong>NEXT STEPS:</strong></h3>
<ol>
<li><strong>Confirm</strong> your attendance by replying to this email</li>
<li><strong>Check</strong> your calendar for the interview invitation</li>
<li><strong>Arrive</strong> 5 minutes early to ensure a smooth start</li>
</ol>

<p>We look forward to meeting you and learning more about your experience and how you can contribute to our team.</p>

<p><strong>Best regards,</strong><br>
<strong>{company_name} Hiring Team</strong></p>

<hr>
<p><em>This is an automated message. Please reply to this email if you have any questions.</em></p>"""
        
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
        """Generate manager notification email with improved formatting."""
        
        subject = f"New Candidate Selected for {job_title} - {candidate_name}"
        
        body = f"""<p><strong>Hi Hiring Manager,</strong></p>

<p>A new candidate has been selected for the <strong>{job_title}</strong> position through our AI-powered screening system.</p>

<h3><strong>CANDIDATE DETAILS:</strong></h3>
<ul>
<li><strong>Name:</strong> {candidate_name}</li>
<li><strong>Position:</strong> {job_title}</li>
<li><strong>Match Score:</strong> {match_score}</li>
<li><strong>Interview Scheduled:</strong> {interview_date} at {interview_time}</li>
</ul>

<h3><strong>WHAT HAPPENS NEXT:</strong></h3>
<ol>
<li><strong>Candidate notification</strong> - Candidate has been notified via email</li>
<li><strong>Calendar scheduling</strong> - Interview has been scheduled in your calendar</li>
<li><strong>Invitations sent</strong> - Calendar invites sent to all participants</li>
</ol>

<h3><strong>CANDIDATE SUMMARY:</strong></h3>
<p>The AI system has analyzed the candidate's resume, GitHub profile, and project portfolio. Based on the comprehensive assessment, this candidate shows <strong>strong alignment</strong> with our requirements.</p>

<h3><strong>INTERVIEW PREPARATION:</strong></h3>
<ul>
<li>Review the candidate's full analysis in the output directory</li>
<li>Check their GitHub profile for recent activity and code quality</li>
<li>Prepare technical questions based on their skill set</li>
<li>Consider their match score and assessment details</li>
</ul>

<h3><strong>CALENDAR EVENT:</strong></h3>
<p>The interview has been automatically scheduled in your <strong>Google Calendar</strong>. You can modify the event or add additional participants as needed.</p>

<h3><strong>NEED TO MAKE CHANGES?</strong></h3>
<ul>
<li><strong>Reschedule:</strong> Modify the calendar event directly</li>
<li><strong>Add participants:</strong> Edit the calendar event</li>
<li><strong>Cancel:</strong> Contact the candidate directly or use the calendar event</li>
</ul>

<p>Let me know if you need any additional information about the candidate or have questions about the interview process.</p>

<p><strong>Best regards,</strong><br>
<strong>AI Hiring Assistant</strong></p>

<hr>
<p><em>This is an automated notification from the GitHub Portia hiring system.</em></p>"""
        
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
        """Generate calendar event description with improved formatting."""
        
        return f"""**Interview for {job_title} Position**

## **INTERVIEW DETAILS:**
• **Candidate:** {candidate_name}
• **Position:** {job_title}
• **Date:** {interview_date}
• **Time:** {interview_time}
• **Duration:** 1 hour
• **Format:** Video call

## **PREPARATION NOTES:**
• Review candidate's resume and GitHub profile
• Check their technical projects and contributions
• Prepare questions based on their skill set
• Have the job description ready for reference

## **TECHNICAL SETUP:**
• Ensure video conferencing software is ready
• Test audio and video equipment
• Have screen sharing capability available
• Prepare any technical assessment materials

## **INTERVIEW STRUCTURE:**
1. **Introduction and company overview** (5 minutes)
2. **Technical discussion and project review** (30 minutes)
3. **Behavioral questions and culture fit** (15 minutes)
4. **Candidate questions** (10 minutes)

## **NEXT STEPS:**
• Prepare feedback form for post-interview evaluation
• Schedule follow-up if needed

---
*This event was automatically created by the GitHub Portia hiring system.*"""
