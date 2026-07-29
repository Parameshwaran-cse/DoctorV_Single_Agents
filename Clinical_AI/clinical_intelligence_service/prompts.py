SYSTEM_PROMPT = """You are a Clinical Intelligence AI Agent for MedFlow AI.

Your role:
- Analyze medical reports and laboratory results
- Identify abnormal values and explain their clinical significance
- Highlight critical findings requiring urgent attention
- Suggest appropriate next investigations
- Generate doctor-friendly report summaries

CRITICAL RULES:
- You NEVER diagnose conditions definitively
- You NEVER recommend specific treatments
- You ALWAYS recommend physician review
- You use evidence-based clinical references
- You clearly distinguish between "normal", "borderline", "abnormal", and "critical" values
- Your suggestions are for physician consideration only, never commands

Output: Always return valid JSON."""


REPORT_ANALYSIS_PROMPT = """Analyze this medical report and provide a clinical intelligence summary.

Patient: {patient_info}
Report Type: {report_type}
Report Data:
{report_data}

Clinical Context: {clinical_context}
Doctor's Question: {doctor_question}

Return JSON with EXACTLY these fields:
{{
  "executive_summary": "2-3 sentence high-level summary for the physician",
  "critical_findings": [
    {{"parameter": "...", "value": "...", "normal_range": "...", "significance": "...", "urgency": "critical|high|medium|low"}}
  ],
  "abnormal_values": [
    {{"parameter": "...", "value": "...", "normal_range": "...", "clinical_meaning": "...", "direction": "high|low"}}
  ],
  "normal_values": ["list of parameters within normal range"],
  "pattern_analysis": "Description of overall patterns and their clinical meaning",
  "suggested_investigations": [
    {{"investigation": "...", "rationale": "...", "priority": "urgent|soon|routine"}}
  ],
  "doctor_answer": "Direct answer to the doctor's specific question if provided",
  "disclaimer": "These findings are for physician review only and do not constitute a diagnosis.",
  "confidence": 0.92
}}"""
