import json
from typing import Dict, Any
from app.schemas import PatientIntakeRequest, PatientIntakeResponse
from app.gemini_service import gemini_service

SYSTEM_PROMPT = """You are a Patient Intake AI Agent for MedFlow AI, an advanced hospital information system.

Your role:
- Collect comprehensive patient information in a structured, empathetic manner
- Identify red flags and urgent symptoms that require immediate attention
- Generate consultation-ready patient summaries for physicians
- Extract allergies, medications, and medical history accurately

Critical rules:
- You NEVER diagnose patients
- You NEVER prescribe medications
- You ALWAYS flag emergency symptoms for immediate physician attention
- You maintain patient confidentiality
- You are clinical, professional, and empathetic

Output format: Always return valid JSON matching the specified schema."""

INTAKE_SUMMARY_PROMPT = """Generate a comprehensive, consultation-ready patient intake summary.

Patient Information:
{patient_data}

Return a JSON object with EXACTLY these fields:
{{
  "consultation_summary": "Doctor-facing comprehensive summary (2-3 paragraphs)",
  "chief_complaint": "One-sentence chief complaint",
  "red_flags": ["list of urgent/emergency findings if any"],
  "allergies_extracted": ["list of confirmed allergies"],
  "medications_extracted": ["list of current medications with doses"],
  "history_summary": "Condensed medical history",
  "recommended_investigations": ["list of suggested diagnostic workup"],
  "triage_priority": "emergency|urgent|semi-urgent|routine",
  "triage_reason": "reason for triage priority",
  "follow_up_questions": ["2-3 intelligent follow-up questions to ask the patient"],
  "confidence": 0.95
}}

Be thorough. Flag all red flags. Never diagnose."""

class PatientIntakeAgent:
    async def run(self, request: PatientIntakeRequest) -> PatientIntakeResponse:
        patient_data = {
            "name": f"{request.first_name} {request.last_name}",
            "dob": request.date_of_birth,
            "gender": request.gender,
            "chief_complaint": request.chief_complaint,
            "symptoms": request.symptoms,
            "symptom_duration": request.symptom_duration,
            "symptom_severity": request.symptom_severity,
            "allergies": request.allergies,
            "current_medications": request.current_medications,
            "medical_history": request.medical_history,
            "surgical_history": request.surgical_history,
            "family_history": request.family_history,
            "social_history": request.social_history,
            "vital_signs": request.vital_signs.model_dump() if request.vital_signs else {},
        }

        result = await gemini_service.complete_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=INTAKE_SUMMARY_PROMPT.format(
                patient_data=json.dumps(patient_data, indent=2)
            ),
            fallback={"error": "Patient intake analysis failed", "confidence": 0.0},
        )
        
        if "error" in result:
            raise RuntimeError(result["error"])

        result["patient_name"] = f"{request.first_name} {request.last_name}"
        return PatientIntakeResponse(**result)

patient_intake_agent = PatientIntakeAgent()
