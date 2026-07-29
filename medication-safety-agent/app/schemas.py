from typing import List, Optional
from pydantic import BaseModel, Field

class MedicationSafetyRequest(BaseModel):
    medications: List[str] = Field(..., example=["Warfarin", "Ibuprofen"])
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    patient_weight_kg: Optional[float] = None
    kidney_function: Optional[str] = None
    liver_function: Optional[str] = None
    pregnancy_status: Optional[bool] = False
    breastfeeding: Optional[bool] = False
    allergies: List[str] = Field(default_factory=list)

class InteractionWarning(BaseModel):
    drug_1: str
    drug_2: str
    severity: str
    explanation: str

class MedicationSafetyResponse(BaseModel):
    is_safe: bool
    interactions: List[InteractionWarning]
