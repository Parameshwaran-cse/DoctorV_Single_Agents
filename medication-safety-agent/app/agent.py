import json
from app.schemas import MedicationSafetyRequest, MedicationSafetyResponse
from app.gemini_service import gemini_service

SYSTEM_PROMPT = """You are a Medication Safety AI Agent for MedFlow AI.

Your role:
- Check for dangerous drug-drug interactions among a list of medications
- Consider patient context (age, organ function, allergies) if provided
- Identify any serious risks

CRITICAL RULES:
- Return warnings with clear severity levels: CRITICAL, HIGH, MODERATE, LOW
- Always explain the mechanism/clinical effect of the interaction
- You are a safety screening tool, NOT a prescriber
- Output must be valid JSON matching the exact schema requested"""

MEDICATION_CHECK_PROMPT = """Perform a medication safety analysis.

Patient Profile:
- Age: {patient_age}
- Gender: {patient_gender}
- Weight (kg): {patient_weight}
- Kidney Function: {kidney_function}
- Liver Function: {liver_function}
- Pregnancy: {pregnancy_status}
- Breastfeeding: {breastfeeding}
- Known Allergies: {allergies}

Medications to Check:
{medications}

Return a JSON object with EXACTLY these fields:
{{
  "is_safe": true or false (false if there are CRITICAL or HIGH interactions),
  "interactions": [
    {{
      "drug_1": "...",
      "drug_2": "...",
      "severity": "CRITICAL|HIGH|MODERATE|LOW",
      "explanation": "Mechanism and clinical effect of the interaction"
    }}
  ]
}}
"""

class MedicationSafetyAgent:
    async def run(self, request: MedicationSafetyRequest) -> MedicationSafetyResponse:
        result = await gemini_service.complete_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=MEDICATION_CHECK_PROMPT.format(
                patient_age=request.patient_age or "Unknown",
                patient_gender=request.patient_gender or "Unknown",
                patient_weight=request.patient_weight_kg or "Unknown",
                kidney_function=request.kidney_function or "Unknown",
                liver_function=request.liver_function or "Unknown",
                pregnancy_status="Yes" if request.pregnancy_status else "No",
                breastfeeding="Yes" if request.breastfeeding else "No",
                allergies=", ".join(request.allergies) if request.allergies else "None",
                medications=", ".join(request.medications)
            ),
            fallback={"is_safe": False, "interactions": []},
        )
        return MedicationSafetyResponse(**result)

medication_safety_agent = MedicationSafetyAgent()
