from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: str
    password: str

class DocumentType(str, Enum):
    SOAP = "soap"
    CLINICAL_NOTE = "clinical_note"
    DISCHARGE_SUMMARY = "discharge_summary"
    REFERRAL_LETTER = "referral_letter"
    INSURANCE_SUMMARY = "insurance_summary"
    VISIT_SUMMARY = "visit_summary"


class DocumentationRequest(BaseModel):
    """Request body for documentation generation."""
    document_type: DocumentType = Field(..., example="soap")
    patient_name: str = Field(..., example="John Doe")
    patient_age: Optional[int] = Field(None, example=45)
    patient_gender: Optional[str] = Field(None, example="male")
    doctor_name: Optional[str] = Field(None, example="Dr. Sarah Chen")
    department: Optional[str] = Field(None, example="Cardiology")

    chief_complaint: Optional[str] = Field(None)
    symptoms: Optional[List[str]] = Field(default_factory=list)
    physical_examination: Optional[str] = Field(None)
    diagnosis: Optional[str] = Field(None)
    treatment_plan: Optional[str] = Field(None)
    medications: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)
    lab_findings: Optional[str] = Field(None)
    imaging_findings: Optional[str] = Field(None)
    medical_history: Optional[str] = Field(None)

    # For referral letters
    referring_to: Optional[str] = Field(None, example="Dr. James Wilson, Cardiologist")
    referral_reason: Optional[str] = Field(None)

    # For discharge summaries
    admission_date: Optional[str] = Field(None)
    discharge_date: Optional[str] = Field(None)
    hospital_course: Optional[str] = Field(None)
    discharge_instructions: Optional[str] = Field(None)

    additional_notes: Optional[str] = Field(None)
