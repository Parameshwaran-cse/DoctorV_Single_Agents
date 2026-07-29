from app.schemas import ScheduleRequest, ScheduleResponse
from app.gemini_service import gemini_service
from app.database import SessionLocal, Appointment

SYSTEM_PROMPT = """You are a Smart Scheduling AI Agent.
Your role is to book appointments and avoid double-booking by checking existing bookings.
If the requested slot conflicts with an existing booking, you MUST return status "CONFLICT" and suggest alternative_slots.
If the requested slot is free, return status "CONFIRMED" and the confirmed_slot.
Output MUST be valid JSON."""

SCHEDULE_BOOK_PROMPT = """Book an appointment.

Patient: {patient_name}
Doctor: {doctor_name}
Preferred Date: {preferred_date}
Preferred Time: {preferred_time}
Reason: {reason}

Existing Bookings for this Doctor on this Date:
{existing_bookings}

Return EXACTLY this JSON:
{{
  "status": "CONFIRMED",
  "message": "string",
  "confirmed_slot": {{"date": "YYYY-MM-DD", "time": "HH:MM"}},
  "alternative_slots": []
}}
If there is a conflict, status should be "CONFLICT", confirmed_slot should be null, and alternative_slots should contain 2 suggestions.
"""

class SmartSchedulingAgent:
    async def run(self, request: ScheduleRequest) -> ScheduleResponse:
        db = SessionLocal()
        try:
            # Fetch existing bookings for this doctor and date
            existing = db.query(Appointment).filter(
                Appointment.doctor_name == request.doctor_name,
                Appointment.date == request.preferred_date
            ).all()
            
            existing_text = "\n".join([f"- {appt.time} (Patient: {appt.patient_name})" for appt in existing])
            if not existing_text:
                existing_text = "None"

            # Call Gemini
            result = await gemini_service.complete_json(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=SCHEDULE_BOOK_PROMPT.format(
                    patient_name=request.patient_name,
                    doctor_name=request.doctor_name,
                    preferred_date=request.preferred_date,
                    preferred_time=request.preferred_time,
                    reason=request.reason,
                    existing_bookings=existing_text
                ),
                fallback={"status": "CONFLICT", "message": "Failed to schedule", "alternative_slots": []}
            )

            response = ScheduleResponse(**result)

            # If Gemini confirmed it, save to SQLite
            if response.status == "CONFIRMED" and response.confirmed_slot:
                new_appt = Appointment(
                    doctor_name=request.doctor_name,
                    date=response.confirmed_slot.date,
                    time=response.confirmed_slot.time,
                    patient_name=request.patient_name
                )
                db.add(new_appt)
                db.commit()

            return response
        finally:
            db.close()

smart_scheduling_agent = SmartSchedulingAgent()
