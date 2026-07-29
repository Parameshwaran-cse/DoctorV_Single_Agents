import os
import json
from datetime import date
from typing import Any, Dict
from dotenv import load_dotenv

from google import genai
from google.genai import types

from schemas import DocumentationRequest, DocumentType
import prompts

# Load environment variables
load_dotenv()

# ─── Provider Clients (lazy-initialised) ────────────────────────────────────

_gemini_client = None
_groq_client    = None
_openai_client  = None

def _get_gemini():
    global _gemini_client
    if _gemini_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client

def _get_groq():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set")
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def _get_openai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client

# ─── Prompt Map ──────────────────────────────────────────────────────────────

PROMPT_MAP = {
    DocumentType.SOAP:             prompts.SOAP_NOTE_PROMPT,
    DocumentType.CLINICAL_NOTE:    prompts.CLINICAL_NOTE_PROMPT,
    DocumentType.DISCHARGE_SUMMARY: prompts.DISCHARGE_SUMMARY_PROMPT,
    DocumentType.REFERRAL_LETTER:  prompts.REFERRAL_LETTER_PROMPT,
    DocumentType.INSURANCE_SUMMARY: prompts.INSURANCE_SUMMARY_PROMPT,
    DocumentType.VISIT_SUMMARY:    prompts.VISIT_SUMMARY_PROMPT,
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def validate_and_sanitize(value: Any, field_name: str) -> str:
    if not value:
        return "Not provided"
    return str(value).strip()


def _build_prompt(request: DocumentationRequest) -> str:
    """Build the full prompt string from the request."""
    today = date.today().strftime("%B %d, %Y")
    prompt_template = PROMPT_MAP.get(request.document_type, prompts.SOAP_NOTE_PROMPT)

    user_prompt = prompt_template.format(
        patient_name=request.patient_name,
        patient_age=request.patient_age or "Unknown",
        patient_gender=request.patient_gender or "Unknown",
        doctor_name=request.doctor_name or "[Doctor Name]",
        department=request.department or "[Department]",
        date=today,
        chief_complaint=validate_and_sanitize(request.chief_complaint or "Not provided", "chief_complaint"),
        symptoms=", ".join(request.symptoms or []) or "Not specified",
        physical_examination=validate_and_sanitize(request.physical_examination or "Not provided", "PE"),
        diagnosis=validate_and_sanitize(request.diagnosis or "Pending", "diagnosis"),
        treatment_plan=validate_and_sanitize(request.treatment_plan or "Pending", "treatment"),
        medications="\n".join(f"- {m}" for m in (request.medications or [])) or "None listed",
        allergies=", ".join(request.allergies or []) or "NKDA",
        lab_findings=validate_and_sanitize(request.lab_findings or "Pending", "labs"),
        additional_notes=validate_and_sanitize(request.additional_notes or "None", "notes"),
        referring_to=request.referring_to or "[Specialist]",
        referral_reason=validate_and_sanitize(request.referral_reason or "See clinical summary", "referral"),
        admission_date=request.admission_date or "Unknown",
        discharge_date=request.discharge_date or today,
        hospital_course=validate_and_sanitize(request.hospital_course or "Not provided", "hospital_course"),
        discharge_instructions=validate_and_sanitize(request.discharge_instructions or "Standard discharge", "discharge"),
        follow_up="As directed by physician",
        timestamp=today,
    )
    return f"{prompts.SYSTEM_PROMPT}\n\n{user_prompt}"


# ─── Provider Runners ────────────────────────────────────────────────────────

def _run_gemini(full_prompt: str) -> Dict[str, Any]:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    client = _get_gemini()
    response = client.models.generate_content(
        model=model,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    result_json = response.text
    if not result_json:
        raise ValueError("Empty response from Gemini")
    return json.loads(result_json)


def _run_groq(full_prompt: str) -> Dict[str, Any]:
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = _get_groq()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    result_json = response.choices[0].message.content
    if not result_json:
        raise ValueError("Empty response from Groq")
    return json.loads(result_json)


def _run_openai(full_prompt: str) -> Dict[str, Any]:
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    client = _get_openai()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    result_json = response.choices[0].message.content
    if not result_json:
        raise ValueError("Empty response from OpenAI")
    return json.loads(result_json)


# Map of provider name → runner function
PROVIDER_RUNNERS = {
    "gemini": _run_gemini,
    "groq":   _run_groq,
    "openai": _run_openai,
}

# Fallback order when the primary provider fails
FALLBACK_ORDER = ["gemini", "groq", "openai"]


# ─── Agent Class ─────────────────────────────────────────────────────────────

class MedicalDocumentationAgent:
    """
    Multi-Provider Medical Documentation Agent.
    Supports Gemini, Groq, and OpenAI. Falls back automatically if primary fails.
    """

    @property
    def agent_name(self) -> str:
        return "Medical Documentation Agent"

    @staticmethod
    def get_active_provider() -> str:
        return os.environ.get("ACTIVE_AI_PROVIDER", "gemini").lower()

    @staticmethod
    def set_active_provider(provider: str) -> None:
        provider = provider.lower()
        if provider not in PROVIDER_RUNNERS:
            raise ValueError(f"Unknown provider: {provider}. Choose from: {list(PROVIDER_RUNNERS.keys())}")
        os.environ["ACTIVE_AI_PROVIDER"] = provider

    def run(self, request: DocumentationRequest) -> Dict[str, Any]:
        """
        Generate clinical documentation using the active AI provider.
        Falls back through remaining providers if the primary one fails.
        """
        full_prompt = _build_prompt(request)
        primary = self.get_active_provider()

        # Build ordered list: primary first, then others as fallbacks
        order = [primary] + [p for p in FALLBACK_ORDER if p != primary]
        last_error = None

        for provider in order:
            runner = PROVIDER_RUNNERS.get(provider)
            if runner is None:
                continue
            try:
                print(f"[Agent] Trying provider: {provider}")
                result = runner(full_prompt)
                result["_provider_used"] = provider
                return result
            except Exception as e:
                print(f"[Agent] Provider '{provider}' failed: {e}")
                last_error = e
                continue

        # All providers failed
        return {
            "error": "Documentation generation failed on all providers",
            "details": str(last_error),
            "confidence": 0.0,
        }


# Singleton instance
medical_documentation_agent = MedicalDocumentationAgent()
