from fastapi import FastAPI
from app.schemas import ScheduleRequest, ScheduleResponse
from app.agent import smart_scheduling_agent
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Smart Scheduling Agent")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/schedule", response_model=ScheduleResponse)
async def process_schedule(request: ScheduleRequest):
    return await smart_scheduling_agent.run(request)
