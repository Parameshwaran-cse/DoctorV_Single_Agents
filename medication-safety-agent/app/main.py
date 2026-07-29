from fastapi import FastAPI
from app.schemas import MedicationSafetyRequest, MedicationSafetyResponse
from app.agent import medication_safety_agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Medication Safety Agent")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/check-interactions", response_model=MedicationSafetyResponse)
async def process_check(request: MedicationSafetyRequest):
    return await medication_safety_agent.run(request)
