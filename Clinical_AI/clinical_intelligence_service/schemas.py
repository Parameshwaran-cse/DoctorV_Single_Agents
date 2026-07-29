from typing import List, Optional
from pydantic import BaseModel, Field


class LabValue(BaseModel):
    parameter: str = Field(..., example="HbA1c")
    value: str = Field(..., example="8.5%")
    normal_range: Optional[str] = Field(None, example="4.0–5.6%")
    unit: Optional[str] = Field(None, example="%")
    status: Optional[str] = Field(None, example="HIGH")


class ClinicalAnalyzeRequest(BaseModel):
    """Request body for clinical report analysis."""
    patient_id: Optional[str] = Field(None)
    patient_name: Optional[str] = Field(None, example="John Doe")
    patient_age: Optional[int] = Field(None, ge=0, le=150, example=45)
    patient_gender: Optional[str] = Field(None, example="male")
    report_type: str = Field(..., example="blood_panel")  # blood_panel, ecg, xray, mri, urine, pathology
    report_text: Optional[str] = Field(None, example="CBC Report: WBC 12.5, RBC 4.2, Hgb 11.0...")
    lab_values: Optional[List[LabValue]] = Field(default_factory=list)
    clinical_context: Optional[str] = Field(None, example="Patient with known diabetes and hypertension")
    doctor_question: Optional[str] = Field(None, example="Are there any critical findings?")


class LoginRequest(BaseModel):
    email: str = Field(..., example="doctor@medflow.ai")
    password: str = Field(..., example="password123")


class SignupRequest(BaseModel):
    name: str = Field(..., example="Dr. Smith")
    email: str = Field(..., example="doctor@medflow.ai")
    password: str = Field(..., example="password123")


class SetProviderRequest(BaseModel):
    """Request body for switching the active AI provider."""
    provider_id: str = Field(..., example="groq", description="One of: gemini_primary, gemini_fallback, groq")
