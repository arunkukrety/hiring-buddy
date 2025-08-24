"""Candidate tracking system for logging hiring information."""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CandidateRecord(BaseModel):
    """Structured candidate record for tracking."""
    
    # basic info
    candidate_name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Candidate's email address")
    phone: str = Field(description="Candidate's phone number")
    linkedin: str = Field(description="LinkedIn profile URL")
    github: str = Field(description="GitHub profile URL")
    
    # job info
    position: str = Field(description="Job title/position")
    company: str = Field(description="Company name")
    match_score: float = Field(description="AI match score percentage")
    
    # timeline
    resume_received_date: str = Field(description="Date resume was received")
    analysis_date: str = Field(description="Date analysis was completed")
    decision_date: Optional[str] = Field(description="Date decision was made", default=None)
    interview_date: Optional[str] = Field(description="Scheduled interview date", default=None)
    interview_time: Optional[str] = Field(description="Scheduled interview time", default=None)
    
    # status
    status: str = Field(description="Current status: received, analyzed, invited, rejected, hired")
    decision: Optional[str] = Field(description="Decision: yes, no, pending", default=None)
    
    # interview details
    google_meet_link: Optional[str] = Field(description="Google Meet link for interview", default=None)
    calendar_event_id: Optional[str] = Field(description="Google Calendar event ID", default=None)
    
    # assessment details
    skill_match_score: Optional[float] = Field(description="Skill match score", default=None)
    experience_relevance_score: Optional[float] = Field(description="Experience relevance score", default=None)
    github_activity_score: Optional[float] = Field(description="GitHub activity score", default=None)
    code_quality_score: Optional[float] = Field(description="Code quality score", default=None)
    
    # notes
    strengths: Optional[List[str]] = Field(description="Candidate strengths", default=None)
    weaknesses: Optional[List[str]] = Field(description="Candidate weaknesses", default=None)
    recommendations: Optional[List[str]] = Field(description="Recommendations", default=None)
    notes: Optional[str] = Field(description="Additional notes", default=None)
    
    # file paths
    resume_file: str = Field(description="Path to resume file")
    analysis_file: Optional[str] = Field(description="Path to analysis results", default=None)


class CandidateTracker:
    """Tool for tracking candidate information throughout the hiring process."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.tracking_file = self.output_dir / "candidate_tracking.json"
        self.csv_file = self.output_dir / "candidate_tracking.csv"
        
        # initialize tracking file if it doesn't exist
        if not self.tracking_file.exists():
            self._initialize_tracking_file()
    
    def _initialize_tracking_file(self):
        """Initialize the tracking file with empty structure."""
        tracking_data = {
            "candidates": [],
            "last_updated": datetime.now().isoformat(),
            "total_candidates": 0
        }
        with open(self.tracking_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)
    
    def log_resume_received(
        self,
        candidate_info: Dict[str, Any],
        resume_file: str,
        job_description: Any
    ) -> str:
        """Log when a resume is received."""
        
        record = CandidateRecord(
            candidate_name=candidate_info.get('candidate_name', 'Unknown'),
            email=candidate_info.get('email', ''),
            phone=candidate_info.get('phone', ''),
            linkedin=candidate_info.get('linkedin', ''),
            github=candidate_info.get('github', ''),
            position=job_description.title,
            company=job_description.company or "Our Company",
            match_score=0.0,  # Will be updated after analysis
            resume_received_date=datetime.now().strftime("%Y-%m-%d"),
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            status="received",
            resume_file=resume_file
        )
        
        # add to tracking
        self._add_candidate_record(record)
        
        print(f"📝 Logged resume received for {record.candidate_name}")
        return record.candidate_name
    
    def update_analysis_results(
        self,
        candidate_name: str,
        analysis_results: Dict[str, Any],
        analysis_file: str
    ) -> bool:
        """Update tracking with analysis results."""
        
        # find existing record
        record = self._find_candidate_record(candidate_name)
        if not record:
            print(f"⚠️ No tracking record found for {candidate_name}")
            return False
        
        # update with analysis results
        record.match_score = analysis_results.get('overall_score', 0.0)
        record.skill_match_score = analysis_results.get('skill_match_score', 0.0)
        record.experience_relevance_score = analysis_results.get('experience_relevance_score', 0.0)
        record.github_activity_score = analysis_results.get('github_activity_score', 0.0)
        record.code_quality_score = analysis_results.get('code_quality_score', 0.0)
        record.strengths = analysis_results.get('strengths', [])
        record.weaknesses = analysis_results.get('weaknesses', [])
        record.recommendations = analysis_results.get('recommendations', [])
        record.analysis_file = analysis_file
        record.status = "analyzed"
        record.analysis_date = datetime.now().strftime("%Y-%m-%d")
        
        # update tracking
        self._update_candidate_record(record)
        
        print(f"📊 Updated analysis results for {candidate_name}")
        return True
    
    def log_decision(
        self,
        candidate_name: str,
        decision: str,
        interview_date: Optional[str] = None,
        interview_time: Optional[str] = None,
        google_meet_link: Optional[str] = None,
        calendar_event_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Log the hiring decision."""
        
        # find existing record
        record = self._find_candidate_record(candidate_name)
        if not record:
            print(f"⚠️ No tracking record found for {candidate_name}")
            return False
        
        # update with decision
        record.decision = decision
        record.decision_date = datetime.now().strftime("%Y-%m-%d")
        record.notes = notes
        
        if decision.lower() in ['yes', 'y', 'invite', 'proceed']:
            record.status = "invited"
            record.interview_date = interview_date
            record.interview_time = interview_time
            record.google_meet_link = google_meet_link
            record.calendar_event_id = calendar_event_id
        elif decision.lower() in ['no', 'n', 'reject']:
            record.status = "rejected"
        
        # update tracking
        self._update_candidate_record(record)
        
        print(f"📋 Logged decision for {candidate_name}: {decision}")
        return True
    
    def _add_candidate_record(self, record: CandidateRecord):
        """Add a new candidate record to tracking."""
        tracking_data = self._load_tracking_data()
        tracking_data["candidates"].append(record.model_dump())
        tracking_data["total_candidates"] = len(tracking_data["candidates"])
        tracking_data["last_updated"] = datetime.now().isoformat()
        self._save_tracking_data(tracking_data)
    
    def _update_candidate_record(self, updated_record: CandidateRecord):
        """Update an existing candidate record."""
        tracking_data = self._load_tracking_data()
        
        for i, candidate in enumerate(tracking_data["candidates"]):
            if candidate["candidate_name"] == updated_record.candidate_name:
                tracking_data["candidates"][i] = updated_record.model_dump()
                tracking_data["last_updated"] = datetime.now().isoformat()
                self._save_tracking_data(tracking_data)
                return
        
        print(f"⚠️ Could not find candidate {updated_record.candidate_name} to update")
    
    def _find_candidate_record(self, candidate_name: str) -> Optional[CandidateRecord]:
        """Find a candidate record by name."""
        tracking_data = self._load_tracking_data()
        
        for candidate in tracking_data["candidates"]:
            if candidate["candidate_name"] == candidate_name:
                return CandidateRecord(**candidate)
        
        return None
    
    def _load_tracking_data(self) -> Dict[str, Any]:
        """Load tracking data from file."""
        if not self.tracking_file.exists():
            self._initialize_tracking_file()
        
        with open(self.tracking_file, 'r') as f:
            return json.load(f)
    
    def _save_tracking_data(self, tracking_data: Dict[str, Any]):
        """Save tracking data to file."""
        with open(self.tracking_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)
        
        # also update CSV file
        self._update_csv_file(tracking_data)
    
    def _update_csv_file(self, tracking_data: Dict[str, Any]):
        """Update CSV file for easy import into Google Sheets."""
        if not tracking_data["candidates"]:
            return
        
        # get all field names from the first candidate
        fieldnames = list(tracking_data["candidates"][0].keys())
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for candidate in tracking_data["candidates"]:
                # handle list fields by converting to string
                for key, value in candidate.items():
                    if isinstance(value, list):
                        candidate[key] = '; '.join(str(item) for item in value)
                writer.writerow(candidate)
    
    def get_tracking_summary(self) -> Dict[str, Any]:
        """Get a summary of tracking data."""
        tracking_data = self._load_tracking_data()
        
        status_counts = {}
        for candidate in tracking_data["candidates"]:
            status = candidate.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_candidates": tracking_data["total_candidates"],
            "status_counts": status_counts,
            "last_updated": tracking_data["last_updated"]
        }
    
    def export_for_google_sheets(self) -> str:
        """Export tracking data in a format ready for Google Sheets import."""
        csv_path = str(self.csv_file.absolute())
       
        
        return csv_path
