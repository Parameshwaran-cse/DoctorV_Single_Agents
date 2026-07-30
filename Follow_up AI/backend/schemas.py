from typing import List, Optional
from pydantic import BaseModel, Field

class FollowUpRequest(BaseModel):
    """Request body for follow-up care plan generation."""
    patient_name: str = Field(..., example="John Doe")
    patient_age: Optional[int] = Field(None, example=45)
    patient_gender: Optional[str] = Field(None, example="male")
    diagnosis: str = Field(..., example="Type 2 Diabetes Mellitus with Hypertension")
    treatment_given: Optional[str] = Field(None, example="Adjusted Metformin to 1000mg BD, added Amlodipine 5mg OD")
    medications: List[str] = Field(default_factory=list, example=["Metformin 1000mg BD", "Amlodipine 5mg OD"])
    allergies: List[str] = Field(default_factory=list)
    follow_up_duration_weeks: Optional[int] = Field(None, ge=1, le=52, example=4)
    special_instructions: Optional[str] = Field(None)
    language: str = Field(default="english", example="english")
    agent_provider: str = Field(default="gemini", description="Which AI engine to use: gemini, grok, or groq")

class FollowUpResponse(BaseModel):
    """Response wrapper for the follow-up agent."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    execution_time_seconds: float
