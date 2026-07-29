from typing import List, Optional, Dict
from pydantic import BaseModel

class ScheduleRequest(BaseModel):
    patient_name: str
    doctor_name: str
    preferred_date: str
    preferred_time: str
    reason: Optional[str] = "Routine Checkup"

class Slot(BaseModel):
    date: str
    time: str

class ScheduleResponse(BaseModel):
    status: str
    confirmed_slot: Optional[Slot] = None
    alternative_slots: Optional[List[Slot]] = None
    message: str
