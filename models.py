from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PersonalDetails(BaseModel):
    full_name: str = Field(..., description="Full name of the applicant")
    email: str = Field(..., description="Email address")
    location: str = Field(..., description="Location/Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")

class WorkExperience(BaseModel):
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD) or 'Present'")
    technologies: Optional[str] = Field(None, description="Technologies used")

class SalaryPreferences(BaseModel):
    preferred_rate: float = Field(..., description="Preferred hourly rate")
    minimum_rate: float = Field(..., description="Minimum acceptable rate")
    currency: str = Field(..., description="Currency (USD, EUR, etc.)")
    availability_hours: int = Field(..., description="Availability in hours per week")

class CompressedApplication(BaseModel):
    personal: PersonalDetails
    experience: List[WorkExperience]
    salary: SalaryPreferences

class LLMEvaluation(BaseModel):
    summary: str = Field(..., description="75-word summary of the applicant")
    score: int = Field(..., ge=1, le=10, description="Quality score from 1-10")
    issues: List[str] = Field(default_factory=list, description="Data gaps or inconsistencies")
    follow_ups: List[str] = Field(default_factory=list, description="Suggested follow-up questions")

class ShortlistCriteria(BaseModel):
    experience_qualified: bool
    compensation_qualified: bool
    location_qualified: bool
    total_years_experience: float
    tier_1_experience: bool
    score_reason: str
