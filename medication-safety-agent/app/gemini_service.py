import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("gemini")

class GeminiService:
    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is not configured in .env")
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except ImportError as exc:
                raise RuntimeError("google-genai SDK not installed.") from exc
        return self._client

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        max_attempts = 3
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                text = await self._call_json_mode(system_prompt, user_prompt)
                return self._parse_json(text)
            except Exception as exc:
                last_error = exc
                if attempt < max_attempts:
                    await asyncio.sleep(2 ** (attempt - 1))

        if fallback is not None:
            return fallback
        raise RuntimeError(f"Gemini failed after {max_attempts} attempts: {last_error}") from last_error

    async def _call_json_mode(self, system_prompt: str, user_prompt: str) -> str:
        client = self._get_client()
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

        combined = (
            f"{system_prompt}\n\n"
            "CRITICAL: Your entire response must be valid JSON only.\n\n"
            f"{user_prompt}"
        )

        from google.genai import types
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=model,
                contents=combined,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            ),
        )
        return response.text or ""

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            inner, in_block = [], False
            for line in lines:
                if line.startswith("```") and not in_block:
                    in_block = True
                    continue
                if line.startswith("```") and in_block:
                    break
                if in_block:
                    inner.append(line)
            text = "\n".join(inner).strip()
        return json.loads(text)

gemini_service = GeminiService()
