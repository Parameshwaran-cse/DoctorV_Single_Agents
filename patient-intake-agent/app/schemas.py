from typing import List, Optional
from pydantic import BaseModel, Field

class VitalSigns(BaseModel):
    blood_pressure: Optional[str] = Field(None, example="120/80 mmHg")
    heart_rate: Optional[str] = Field(None, example="72 bpm")
    temperature: Optional[str] = Field(None, example="98.6°F")
    oxygen_saturation: Optional[str] = Field(None, example="98%")
    respiratory_rate: Optional[str] = Field(None, example="16/min")
    weight: Optional[str] = Field(None, example="70 kg")
    height: Optional[str] = Field(None, example="175 cm")

class PatientIntakeRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str = Field(...)
    gender: str = Field(...)
    phone: Optional[str] = None
    email: Optional[str] = None
    chief_complaint: str = Field(..., min_length=5)
    symptoms: List[str] = Field(default_factory=list)
    symptom_duration: Optional[str] = None
    symptom_severity: Optional[int] = Field(None, ge=1, le=10)
    allergies: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    medical_history: Optional[str] = None
    surgical_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    vital_signs: Optional[VitalSigns] = None

class PatientIntakeResponse(BaseModel):
    patient_name: str
    consultation_summary: str
    chief_complaint: str
    red_flags: List[str]
    allergies_extracted: List[str]
    medications_extracted: List[str]
    history_summary: str
    recommended_investigations: List[str]
    triage_priority: str
    triage_reason: str
    follow_up_questions: List[str]
    confidence: float
