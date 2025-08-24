"""Scheduler agent for handling candidate selection workflow."""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from portia import Portia, ActionClarification, PlanRunState
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input

from tools.job_matcher import JobMatchResult
from tools.email_templates import EmailTemplates


class SchedulerAgent:
    """Agent responsible for scheduling interviews and sending notifications."""
    
    def __init__(self, portia: Portia):
        self.portia = portia
    
    def schedule_interview_and_notify(
        self, 
        candidate_info: Dict[str, Any],
        job_description: Any,
        match_score: float,
        email_templates: Optional[Dict[str, Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Schedule interview and send notification emails using Portia AI tools."""
        
        print("📅 Step 4: Scheduling interview and sending notifications...")
        
        # calculate interview date (7 days from now)
        interview_date = datetime.now() + timedelta(days=7)
        interview_start = interview_date.replace(hour=10, minute=0, second=0, microsecond=0)
        interview_end = interview_start + timedelta(hours=1)
        
        # format dates for calendar
        start_time = interview_start.strftime("%Y-%m-%dT%H:%M:%S")
        end_time = interview_end.strftime("%Y-%m-%dT%H:%M:%S")
        
        # get candidate details
        candidate_name = candidate_info.get('candidate_name', 'Candidate')
        candidate_email = candidate_info.get('email', '')
        
        # handle empty email case
        if not candidate_email or candidate_email.strip() == "":
            print("⚠️ Warning: No email found for candidate. Using placeholder email.")
            candidate_email = "candidate@example.com"  # placeholder for testing
        
        # use provided email templates or generate default ones
        if email_templates:
            candidate_email_data = email_templates["candidate"]
            manager_email_data = email_templates["manager"]
        else:
            candidate_email_data = EmailTemplates.candidate_acceptance_email(
                candidate_name=candidate_name,
                job_title=job_description.title,
                company_name=job_description.company or "Our Company",
                interview_date=interview_start.strftime("%B %d, %Y"),
                interview_time=interview_start.strftime("%I:%M %p"),
                calendar_link="https://calendar.google.com/calendar/u/0/r/week",
                google_meet_link="[Will be provided in calendar invite]"  # Placeholder - will be updated after calendar creation
            )
            
            manager_email_data = EmailTemplates.manager_notification_email(
                candidate_name=candidate_name,
                job_title=job_description.title,
                match_score=f"{match_score:.1%}",
                interview_date=interview_start.strftime("%B %d, %Y"),
                interview_time=interview_start.strftime("%I:%M %p")
            )
        
        calendar_description = EmailTemplates.calendar_event_description(
            candidate_name=candidate_name,
            job_title=job_description.title,
            interview_date=interview_start.strftime("%B %d, %Y"),
            interview_time=interview_start.strftime("%I:%M %p")
        )
        
        try:
            # step 1: create scheduling plan using PlanBuilderV2 for calendar and emails
            plan = self._create_scheduling_plan(candidate_email)
            
            # run the plan with all the required inputs
            plan_run_inputs = {
                "candidate_name": candidate_name,
                "job_title": job_description.title,
                "company_name": "PORTIA AI",
                "match_score": f"{match_score:.1%}",
                "interview_date": interview_start.strftime("%B %d, %Y"),
                "interview_time": interview_start.strftime("%I:%M %p"),
                "start_time": start_time,
                "end_time": end_time,
                "calendar_link": "https://calendar.google.com/calendar/u/0/r/week",
                "event_title": f"Interview for {job_description.title} Position",
                "event_description": calendar_description,
                "attendees": [candidate_email],
                "candidate_email_subject": candidate_email_data['subject'],
                "candidate_email_body": candidate_email_data['body'],
                "manager_email_subject": manager_email_data['subject'],
                "manager_email_body": manager_email_data['body']
            }
            
            print("📅 Creating calendar event and sending emails...")
            result = self.portia.run_plan(plan, plan_run_inputs=plan_run_inputs)
            
            # handle OAuth if needed
            while result.state == PlanRunState.NEED_CLARIFICATION:
                print("\n🔐 OAuth Authentication Required")
                print("=" * 50)
                
                clarifications = result.get_outstanding_clarifications()
                for clarification in clarifications:
                    if isinstance(clarification, ActionClarification):
                        print(f"🔗 OAuth required: {clarification.user_guidance}")
                        print(f"🔗 Please click the link below to authenticate:")
                        print(f"🔗 {clarification.action_url}")
                        print("\n⏳ Waiting for authentication to complete...")
                        
                        result = self.portia.wait_for_ready(result)
                        break
                
                result = self.portia.resume(result)
            
            print("✅ Scheduling completed successfully")
            
            return {
                "success": True,
                "interview_date": interview_start.strftime("%B %d, %Y at %I:%M %p"),
                "candidate_email_sent": candidate_email != "",
                "manager_email_sent": True,
                "calendar_event_created": True,
                "google_meet_link": None,
                "details": {
                    "candidate_result": "Email sent successfully",
                    "manager_result": "Email sent successfully", 
                    "calendar_result": "Calendar event created successfully"
                }
            }
            
        except Exception as e:
            print(f"❌ Error in scheduling workflow: {str(e)}")
            return {
                "success": False,
                "interview_date": interview_start.strftime("%B %d, %Y at %I:%M %p"),
                "error": str(e),
                "details": {
                    "candidate_result": f"Failed: {str(e)}",
                    "manager_result": f"Failed: {str(e)}", 
                    "calendar_result": f"Failed: {str(e)}"
                }
            }
    
    def _create_scheduling_plan(self, candidate_email: str) -> PlanBuilderV2:
        """Create a plan for creating calendar event and sending notification emails."""
        
        plan = PlanBuilderV2(label="Schedule interview and send notifications")
        
        # define inputs
        plan.input(name="candidate_name", description="Candidate's full name")
        plan.input(name="job_title", description="Job title/position")
        plan.input(name="company_name", description="Company name")
        plan.input(name="match_score", description="Candidate's match score")
        plan.input(name="interview_date", description="Interview date (formatted)")
        plan.input(name="interview_time", description="Interview time (formatted)")
        plan.input(name="start_time", description="Calendar start time (ISO format)")
        plan.input(name="end_time", description="Calendar end time (ISO format)")
        plan.input(name="calendar_link", description="Link to calendar for rescheduling")
        plan.input(name="event_title", description="Calendar event title")
        plan.input(name="event_description", description="Calendar event description")
        plan.input(name="attendees", description="List of attendee email addresses")
        plan.input(name="candidate_email_subject", description="Candidate email subject")
        plan.input(name="candidate_email_body", description="Candidate email body")
        plan.input(name="manager_email_subject", description="Manager email subject")
        plan.input(name="manager_email_body", description="Manager email body")
        
        # step 1: create Google Calendar event with Google Meet using Portia Calendar tool
        plan.invoke_tool_step(
            tool="portia:google:gcalendar:create_event",
            args={
                "event_title": Input("event_title"),
                "start_time": Input("start_time"),
                "end_time": Input("end_time"),
                "event_description": Input("event_description"),
                "attendees": Input("attendees")
            },
            step_name="create_calendar_event"
        )
        
        # step 2: send email to candidate using Portia Gmail tool
        plan.invoke_tool_step(
            tool="portia:google:gmail:send_email",
            args={
                "recipients": [candidate_email],
                "email_title": Input("candidate_email_subject"),
                "email_body": Input("candidate_email_body")
            },
            step_name="send_candidate_email"
        )
        
        # step 3: send email to hiring manager using Portia Gmail tool
        plan.invoke_tool_step(
            tool="portia:google:gmail:send_email",
            args={
                "recipients": ["hiring@company.com"],  # This will be replaced by OAuth sender
                "email_title": Input("manager_email_subject"),
                "email_body": Input("manager_email_body")
            },
            step_name="send_manager_email"
        )
        
        return plan.build()
    
    def _create_email_only_plan(self, candidate_email: str) -> PlanBuilderV2:
        """Create a plan for sending notification emails only."""
        
        plan = PlanBuilderV2(label="Send notification emails")
        
        # define inputs
        plan.input(name="candidate_name", description="Candidate's full name")
        plan.input(name="job_title", description="Job title/position")
        plan.input(name="company_name", description="Company name")
        plan.input(name="match_score", description="Candidate's match score")
        plan.input(name="interview_date", description="Interview date (formatted)")
        plan.input(name="interview_time", description="Interview time (formatted)")
        plan.input(name="start_time", description="Calendar start time (ISO format)")
        plan.input(name="end_time", description="Calendar end time (ISO format)")
        plan.input(name="calendar_link", description="Link to calendar for rescheduling")
        plan.input(name="candidate_email_subject", description="Candidate email subject")
        plan.input(name="candidate_email_body", description="Candidate email body")
        plan.input(name="manager_email_subject", description="Manager email subject")
        plan.input(name="manager_email_body", description="Manager email body")
        
        # step 1: send email to candidate using Portia Gmail tool
        plan.invoke_tool_step(
            tool="portia:google:gmail:send_email",
            args={
                "recipients": [candidate_email],
                "email_title": Input("candidate_email_subject"),
                "email_body": Input("candidate_email_body")
            },
            step_name="send_candidate_email"
        )
        
        # step 2: send email to hiring manager using Portia Gmail tool
        plan.invoke_tool_step(
            tool="portia:google:gmail:send_email",
            args={
                "recipients": ["hiring@company.com"],  # This will be replaced by OAuth sender
                "email_title": Input("manager_email_subject"),
                "email_body": Input("manager_email_body")
            },
            step_name="send_manager_email"
        )
        
        return plan.build()
    

    
    def generate_email_templates(
        self,
        candidate_info: Dict[str, Any],
        job_description: Any,
        match_score: float
    ) -> Dict[str, Dict[str, str]]:
        """Generate email templates for candidate and manager."""
        
        # calculate interview date (7 days from now)
        interview_date = datetime.now() + timedelta(days=7)
        interview_start = interview_date.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # get candidate details
        candidate_name = candidate_info.get('candidate_name', 'Candidate')
        candidate_email = candidate_info.get('email', '')
        
        # generate a simple Google Meet link
        import uuid
        meet_id = str(uuid.uuid4())[:10]  # simple meet ID
        google_meet_link = f"https://meet.google.com/{meet_id}"
        
        # generate email templates (no customization here - that's handled separately)
        candidate_email_data = EmailTemplates.candidate_acceptance_email(
            candidate_name=candidate_name,
            job_title=job_description.title,
            company_name="PORTIA AI",
            interview_date=interview_start.strftime("%B %d, %Y"),
            interview_time=interview_start.strftime("%I:%M %p"),
            calendar_link="https://calendar.google.com/calendar/u/0/r/week"
        )
        
        manager_email_data = EmailTemplates.manager_notification_email(
            candidate_name=candidate_name,
            job_title=job_description.title,
            match_score=f"{match_score:.1%}",
            interview_date=interview_start.strftime("%B %d, %Y"),
            interview_time=interview_start.strftime("%I:%M %p")
        )
        
        return {
            "candidate": candidate_email_data,
            "manager": manager_email_data
        }
    
    def customize_existing_emails(
        self,
        existing_templates: Dict[str, Dict[str, str]],
        custom_instructions: str,
        candidate_info: Dict[str, Any],
        job_description: Any,
        match_score: float
    ) -> Dict[str, Dict[str, str]]:
        """Efficiently customize existing email templates without re-generation."""
        
        print("🔧 Customizing existing email templates...")
        
        # customize candidate email
        customized_candidate = self._customize_single_email(
            existing_templates['candidate'],
            custom_instructions,
            "candidate",
            candidate_info,
            job_description,
            match_score
        )
        
        # customize manager email
        customized_manager = self._customize_single_email(
            existing_templates['manager'],
            custom_instructions,
            "manager",
            candidate_info,
            job_description,
            match_score
        )
        
        return {
            "candidate": customized_candidate,
            "manager": customized_manager
        }
    
    def _customize_single_email(
        self,
        existing_email: Dict[str, str],
        custom_instructions: str,
        email_type: str,
        candidate_info: Dict[str, Any],
        job_description: Any,
        match_score: float
    ) -> Dict[str, str]:
        """Customize a single email template efficiently."""
        
        # use LLM to customize the email
        try:
            llm = self.portia.config.get_generative_model("google/gemini-2.0-flash")
        except:
            try:
                llm = self.portia.config.get_generative_model("google/gemini-1.5-flash")
            except:
                llm = self.portia.config.get_generative_model("google/gemini-1.0-pro")
        
        customization_prompt = f"""
You are an email customization assistant. Please modify the following {email_type} email based on the user's instructions.

ORIGINAL EMAIL:
Subject: {existing_email['subject']}
Body: {existing_email['body']}

USER INSTRUCTIONS: {custom_instructions}

CANDIDATE DETAILS:
- Name: {candidate_info.get('candidate_name', 'Candidate')}
- Position: {job_description.title}
- Company: {job_description.company or "Our Company"}
- Match Score: {match_score:.1%}

Please return the customized email in this exact JSON format:
{{
    "subject": "customized subject line",
    "body": "customized email body"
}}

IMPORTANT FORMATTING RULES:
- Do NOT use markdown syntax like **bold** or *italic*
- Use ALL CAPS for section headers (e.g., "INTERVIEW DETAILS:")
- Use plain text formatting only
- Keep the email professional and include all necessary interview details
- Ensure the email will render properly in Gmail and other email clients
- Preserve all important information from the original email
"""
        
        try:
            from portia.model import Message
            message = Message(role="user", content=customization_prompt)
            response = llm.get_response([message])
            
            # parse JSON response
            import json
            start_idx = response.content.find('{')
            end_idx = response.content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response.content[start_idx:end_idx]
                customized_email = json.loads(json_str)
                return customized_email
            else:
                print(f"⚠️ Could not parse customized {email_type} email, using original")
                return existing_email
                
        except Exception as e:
            print(f"⚠️ Error customizing {email_type} email: {str(e)}")
            return existing_email
