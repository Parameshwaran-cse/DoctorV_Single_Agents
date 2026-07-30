from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import FollowUpRequest, FollowUpResponse
from agent import agent

app = FastAPI(
    title="Follow-up Care Agent Microservice",
    description="Standalone AI microservice for generating patient follow-up care plans.",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/analyze", response_model=FollowUpResponse)
def analyze_followup(request: FollowUpRequest):
    """
    Generate a personalized post-visit care plan based on patient details.
    """
    try:
        response = agent.run(request)
        if not response.success:
            # We still return 200 with success=False and the error in the body
            # because this is an agent domain error, not necessarily a crash.
            pass
        return response
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
