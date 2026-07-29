import json
import os
from typing import Any, Dict
from google import genai
from google.genai import types
from groq import Groq

from schemas import ClinicalAnalyzeRequest
import prompts


# ---------------------------------------------------------------------------
# Provider Configuration
# ---------------------------------------------------------------------------

PROVIDERS = {
    "gemini_primary": {
        "label": "Gemini 1.5 Flash (Primary)",
        "model": "gemini-1.5-flash",
        "provider_type": "gemini",
        "env_key": "GEMINI_API_KEY",
    },
    "gemini_fallback": {
        "label": "Gemini 1.5 Flash (Fallback / Backup)",
        "model": "gemini-1.5-flash",
        "provider_type": "gemini",
        "env_key": "GEMINI_API_KEY_2",
    },
    "groq": {
        "label": "Groq — LLaMA 3.3 70B",
        "model": "llama-3.3-70b-versatile",
        "provider_type": "groq",
        "env_key": "GROQ_API_KEY",
    },
}


class ProviderConfig:
    """Singleton that holds the currently selected provider (persisted in env)."""

    def __init__(self):
        self._active = os.getenv("ACTIVE_PROVIDER", "gemini_primary")

    @property
    def active(self) -> str:
        return self._active

    @active.setter
    def active(self, value: str):
        if value not in PROVIDERS:
            raise ValueError(f"Unknown provider '{value}'. Choose from: {list(PROVIDERS.keys())}")
        self._active = value

    def get_config(self) -> dict:
        cfg = PROVIDERS[self._active]
        api_key = os.getenv(cfg["env_key"], "")
        return {**cfg, "id": self._active, "api_key_configured": bool(api_key)}

    def list_providers(self) -> list:
        result = []
        for pid, cfg in PROVIDERS.items():
            api_key = os.getenv(cfg["env_key"], "")
            result.append({
                "id": pid,
                "label": cfg["label"],
                "model": cfg["model"],
                "provider_type": cfg["provider_type"],
                "api_key_configured": bool(api_key),
                "is_active": pid == self._active,
            })
        return result


# Singleton provider config
provider_config = ProviderConfig()


class ClinicalIntelligenceAgent:
    """
    Standalone Agent: Clinical Intelligence Agent

    Responsibilities:
    - Analyze uploaded reports
    - Explain abnormal values
    - Highlight critical findings
    - Suggest possible next investigations
    - Generate doctor-friendly report summary
    
    Supports multiple AI providers: Gemini (Primary/Fallback) and Groq.
    """

    def __init__(self):
        self.agent_name = "Clinical Intelligence Agent"

    def _sanitize(self, text: str, field_name: str) -> str:
        """Simple sanitization logic."""
        if not text:
            return ""
        return str(text)[:10000]

    def _run_gemini(self, user_prompt: str, api_key: str, model: str) -> Dict[str, Any]:
        """Execute analysis via Google Gemini SDK."""
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=prompts.SYSTEM_PROMPT,
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)

    def _run_groq(self, user_prompt: str, api_key: str, model: str) -> Dict[str, Any]:
        """Execute analysis via Groq API."""
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content)

    def run(self, request: ClinicalAnalyzeRequest) -> Dict[str, Any]:
        """Call the active AI provider for clinical report analysis."""
        report_data = request.report_text or json.dumps(
            [v.model_dump() for v in (request.lab_values or [])], indent=2
        )

        patient_info = f"{request.patient_name or 'Unknown'}, {request.patient_age or 'Unknown'}y {request.patient_gender or ''}"

        user_prompt = prompts.REPORT_ANALYSIS_PROMPT.format(
            patient_info=patient_info,
            report_type=request.report_type,
            report_data=self._sanitize(report_data, "report_data"),
            clinical_context=self._sanitize(request.clinical_context or "None provided", "context"),
            doctor_question=self._sanitize(request.doctor_question or "General analysis", "question"),
        )

        try:
            cfg = provider_config.get_config()
            api_key = os.getenv(cfg["env_key"], "")

            if not api_key:
                return {
                    "error": f"API key not configured for provider '{cfg['id']}'. Please set {cfg['env_key']} in your .env file.",
                    "confidence": 0.0,
                }

            if cfg["provider_type"] == "gemini":
                return self._run_gemini(user_prompt, api_key, cfg["model"])
            elif cfg["provider_type"] == "groq":
                return self._run_groq(user_prompt, api_key, cfg["model"])
            else:
                return {"error": f"Unknown provider type: {cfg['provider_type']}", "confidence": 0.0}

        except Exception as e:
            return {
                "error": f"Clinical analysis failed: {str(e)}",
                "confidence": 0.0,
            }


# Singleton instance
clinical_intelligence_agent = ClinicalIntelligenceAgent()
