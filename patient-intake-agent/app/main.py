from fastapi import FastAPI
from app.schemas import PatientIntakeRequest, PatientIntakeResponse
from app.agent import patient_intake_agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Patient Intake Agent")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/intake", response_model=PatientIntakeResponse)
async def process_intake(request: PatientIntakeRequest):
    return await patient_intake_agent.run(request)
