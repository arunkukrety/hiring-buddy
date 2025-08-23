"""CLI utilities for the GitHub Portia system."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from agents.resume_agent import parse_resume


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


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--resume", required=True, help="path to pdf or plain text resume")
    args = p.parse_args()

    facts = parse_resume(Path(args.resume))
    print(json.dumps(facts.model_dump(), indent=2))


if __name__ == "__main__":
    main()

