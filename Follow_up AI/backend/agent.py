import os
import json
import time
from typing import Any, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types
import openai

from schemas import FollowUpRequest, FollowUpResponse
from prompts import SYSTEM_PROMPT, FOLLOWUP_PLAN_PROMPT

# Load environment variables
load_dotenv()

class FollowUpCareAgent:
    """
    Self-contained Agent 5: Follow-up Care Agent
    """
    
    def __init__(self):
        self.gemini_clients = []
        
        primary_key = os.getenv("GEMINI_API_KEY")
        if primary_key and primary_key != "your_api_key_here":
            self.gemini_clients.append(genai.Client(api_key=primary_key))
            
        self.grok_client = None
        grok_key = os.getenv("GROK_API_KEY")
        if grok_key and grok_key != "your-grok-api-key-here":
            self.grok_client = openai.OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
            
        self.groq_client = None
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key != "your-groq-api-key-here":
            self.groq_client = openai.OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    @property
    def agent_name(self) -> str:
        return "Follow-up Care Agent"

    def run(self, request: FollowUpRequest) -> FollowUpResponse:
        """Call Gemini for personalized follow-up plan with execution timing and error handling."""
        start_time = time.time()
        
        if not self.gemini_clients and not self.grok_client and not self.groq_client:
             return FollowUpResponse(
                success=False,
                error="No valid GEMINI, GROK, or GROQ API keys found. Please check your .env file.",
                execution_time_seconds=0.0
            )
        
        try:
            user_prompt = FOLLOWUP_PLAN_PROMPT.format(
                patient_name=request.patient_name,
                patient_age=request.patient_age or "Unknown",
                patient_gender=request.patient_gender or "Unknown",
                diagnosis=request.diagnosis,
                treatment_given=request.treatment_given or "As documented",
                medications="\n".join(f"- {m}" for m in request.medications) or "None listed",
                allergies=", ".join(request.allergies) or "No known allergies",
                follow_up_duration=request.follow_up_duration_weeks or 4,
                special_instructions=request.special_instructions or "Standard follow-up",
            )
            
            last_error = None
            response_text = None
            
            provider = getattr(request, 'agent_provider', 'gemini').lower()
            
            if provider == "groq" and self.groq_client:
                try:
                    response = self.groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.2,
                        max_tokens=4000
                    )
                    response_text = response.choices[0].message.content
                except Exception as e:
                    last_error = e
            elif provider == "grok" and self.grok_client:
                try:
                    response = self.grok_client.chat.completions.create(
                        model="grok-beta",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.2
                    )
                    response_text = response.choices[0].message.content
                except Exception as e:
                    last_error = e
            elif provider == "gemini" and self.gemini_clients:
                for client in self.gemini_clients:
                    try:
                        response = client.models.generate_content(
                            model=self.model,
                            contents=[
                                types.Part.from_text(text=SYSTEM_PROMPT + "\n\n" + user_prompt)
                            ],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.2
                            )
                        )
                        response_text = response.text
                        break
                    except Exception as e:
                        last_error = e
                        continue
            else:
                last_error = Exception(f"Provider {provider} not initialized or invalid.")

            if not response_text:
                raise last_error or Exception(f"Failed to generate content using {provider}.")
            
            # Clean up the response text before parsing
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Find the first { and last } to extract JSON strictly
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                cleaned_text = cleaned_text[start_idx:end_idx+1]
            
            try:
                result_data = json.loads(cleaned_text)
            except json.JSONDecodeError as jde:
                raise Exception(f"JSON parsing failed: {str(jde)}. The AI model returned malformed JSON structure.")
            
            execution_time = round(time.time() - start_time, 2)
            
            return FollowUpResponse(
                success=True,
                data=result_data,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            return FollowUpResponse(
                success=False,
                error=f"Agent execution failed: {str(e)}",
                execution_time_seconds=execution_time
            )

# Singleton instance
agent = FollowUpCareAgent()
