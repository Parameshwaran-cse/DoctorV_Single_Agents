SYSTEM_PROMPT = """You are a Medical Documentation AI Agent for MedFlow AI.

Your role:
- Generate professional, accurate, and complete medical documents
- Follow standard clinical documentation formats (SOAP, etc.)
- Produce documentation suitable for medical records
- Maintain clinical accuracy and professional language

Document types you generate:
- SOAP Notes (Subjective, Objective, Assessment, Plan)
- Clinical Notes
- Discharge Summaries
- Referral Letters
- Insurance Summaries
- Patient Visit Summaries

RULES:
- Use professional medical terminology
- Be precise and accurate
- Follow standard medical documentation formats
- Never fabricate clinical findings
- Always leave placeholders marked [TO BE COMPLETED BY PHYSICIAN] for missing required info
- Output must be valid JSON"""


SOAP_NOTE_PROMPT = """Generate a complete SOAP Note for the following clinical encounter.

Patient: {patient_name}, {patient_age}y, {patient_gender}
Doctor: {doctor_name}
Department: {department}
Date: {date}

Clinical Data:
- Chief Complaint: {chief_complaint}
- Symptoms: {symptoms}
- Physical Examination: {physical_examination}
- Diagnosis: {diagnosis}
- Treatment Plan: {treatment_plan}
- Medications: {medications}
- Allergies: {allergies}
- Lab/Imaging: {lab_findings}
- Additional Notes: {additional_notes}

Return JSON:
{{
  "document_type": "SOAP Note",
  "title": "SOAP Note — {patient_name} — {date}",
  "sections": {{
    "subjective": {{
      "chief_complaint": "...",
      "history_of_present_illness": "Full HPI in paragraph form",
      "review_of_systems": "Relevant positive and negative findings",
      "past_medical_history": "...",
      "medications": ["list"],
      "allergies": ["list"],
      "social_history": "..."
    }},
    "objective": {{
      "vital_signs": "...",
      "physical_examination": "Detailed PE findings by system",
      "laboratory_results": "...",
      "imaging_results": "..."
    }},
    "assessment": {{
      "primary_diagnosis": "...",
      "differential_diagnoses": ["list"],
      "clinical_impression": "..."
    }},
    "plan": {{
      "investigations": ["list"],
      "medications": ["list with dose/frequency/duration"],
      "procedures": ["list if any"],
      "referrals": ["list if any"],
      "patient_education": "...",
      "follow_up": "...",
      "return_precautions": "..."
    }}
  }},
  "physician_signature_block": "Dr. {doctor_name} | {department} | [Signature Required]",
  "document_status": "draft",
  "confidence": 0.94
}}"""


DISCHARGE_SUMMARY_PROMPT = """Generate a complete Discharge Summary.

Patient: {patient_name}, {patient_age}y, {patient_gender}
Admission Date: {admission_date}
Discharge Date: {discharge_date}
Doctor: {doctor_name}
Department: {department}
Diagnosis: {diagnosis}
Hospital Course: {hospital_course}
Medications: {medications}
Discharge Instructions: {discharge_instructions}

Return JSON:
{{
  "document_type": "Discharge Summary",
  "title": "Discharge Summary — {patient_name}",
  "sections": {{
    "admission_details": {{}},
    "diagnosis": {{}},
    "hospital_course": "...",
    "procedures_performed": [],
    "discharge_medications": [],
    "discharge_condition": "...",
    "follow_up_instructions": {{}},
    "return_to_er_if": []
  }},
  "document_status": "draft",
  "confidence": 0.93
}}"""


REFERRAL_LETTER_PROMPT = """Generate a professional Referral Letter.

From: {doctor_name}, {department}
To: {referring_to}
Patient: {patient_name}, {patient_age}y, {patient_gender}
Reason: {referral_reason}
Diagnosis: {diagnosis}
Current Medications: {medications}
Allergies: {allergies}
Clinical Summary: {chief_complaint}

Return JSON:
{{
  "document_type": "Referral Letter",
  "title": "Referral Letter — {patient_name}",
  "content": "Full professional referral letter text",
  "urgency": "routine|soon|urgent",
  "key_clinical_points": [],
  "document_status": "draft",
  "confidence": 0.95
}}"""


CLINICAL_NOTE_PROMPT = """Generate a Clinical Progress Note.

Patient: {patient_name}, {patient_age}y
Doctor: {doctor_name}
Findings: {chief_complaint}
Assessment: {diagnosis}
Plan: {treatment_plan}

Return JSON:
{{
  "document_type": "Clinical Note",
  "title": "Clinical Note — {patient_name}",
  "content": "Full professional clinical note",
  "key_points": [],
  "document_status": "draft",
  "confidence": 0.93
}}"""


INSURANCE_SUMMARY_PROMPT = """Generate a clinical summary suitable for insurance authorization.

Patient: {patient_name}, {patient_age}y
Diagnosis: {diagnosis}
Treatment: {treatment_plan}
Medications: {medications}
Clinical Justification: {chief_complaint}

Return JSON:
{{
  "document_type": "Insurance Summary",
  "title": "Insurance Authorization Summary — {patient_name}",
  "diagnosis_codes_suggested": [],
  "clinical_necessity_statement": "...",
  "treatment_summary": "...",
  "estimated_duration": "...",
  "physician_attestation": "[Physician signature required]",
  "document_status": "draft",
  "confidence": 0.91
}}"""


VISIT_SUMMARY_PROMPT = """Generate a patient-friendly Visit Summary.

Patient: {patient_name}
Diagnosis: {diagnosis}
Treatment: {treatment_plan}
Medications: {medications}
Next Steps: {follow_up}

Return JSON:
{{
  "document_type": "Patient Visit Summary",
  "title": "Your Visit Summary — {patient_name}",
  "what_we_found": "Plain language explanation of findings",
  "what_this_means": "Simple explanation for the patient",
  "your_medications": [],
  "what_to_do_next": [],
  "when_to_seek_help": [],
  "follow_up_date": "...",
  "contact_information": "Call our clinic at [CLINIC NUMBER] if you have questions",
  "document_status": "draft",
  "confidence": 0.96
}}"""
