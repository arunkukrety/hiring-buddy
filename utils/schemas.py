from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


class _lower:
    """small caps marker"""


class Contact(BaseModel):
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: List[str] = Field(default_factory=list)
    portfolio: List[str] = Field(default_factory=list)
    other_links: List[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    school: str
    degree: str
    start: Optional[str] = None
    end: Optional[str] = None


class ExperienceEntry(BaseModel):
    company: str
    role: str
    start: Optional[str] = None
    end: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str
    link: Optional[str] = None
    description: Optional[str] = None
    tech: List[str] = Field(default_factory=list)


class Skills(BaseModel):
    primary: List[str] = Field(default_factory=list)
    secondary: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CandidateFacts(BaseModel):
    request_id: str
    candidate: Contact
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: List[ProjectEntry] = Field(default_factory=list)
    parse_warnings: List[str] = Field(default_factory=list)

    model_config = {
        "extra": "forbid",
    }

