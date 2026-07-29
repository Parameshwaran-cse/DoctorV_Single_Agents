import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables (e.g., GEMINI_API_KEY) before anything else
load_dotenv()

from schemas import ClinicalAnalyzeRequest, LoginRequest, SignupRequest, SetProviderRequest
from agent import clinical_intelligence_agent, provider_config
from fastapi.middleware.cors import CORSMiddleware
import secrets

app = FastAPI(
    title="Clinical Intelligence Agent Microservice",
    description="Standalone AI microservice for analyzing medical reports and laboratory results.",
    version="2.0.0"
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to track execution time."""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time-Secs"] = f"{process_time:.4f}"
        return response
    except Exception as e:
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error during execution",
                "error": str(e),
                "execution_time_secs": process_time
            },
            headers={"X-Process-Time-Secs": f"{process_time:.4f}"}
        )

# ---------------------------------------------------------------------------
# Auth Endpoints (Mock)
# ---------------------------------------------------------------------------

@app.post("/login", summary="Mock Login")
def login(request: LoginRequest):
    """Mock login endpoint returning a fake token."""
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"token": f"mock_token_{secrets.token_hex(16)}", "user": {"email": request.email, "name": "Dr. Smith"}}

@app.post("/signup", summary="Mock Signup")
def signup(request: SignupRequest):
    """Mock signup endpoint returning a fake token."""
    return {"token": f"mock_token_{secrets.token_hex(16)}", "user": {"email": request.email, "name": request.name}}

# ---------------------------------------------------------------------------
# Clinical Intelligence Endpoint
# ---------------------------------------------------------------------------

@app.post("/analyze", summary="Analyze Clinical Report", response_model=dict)
def analyze_report(request: ClinicalAnalyzeRequest):
    """
    Analyze a medical report using the active Clinical Intelligence Agent provider.
    """
    try:
        result = clinical_intelligence_agent.run(request)

        if "error" in result and result.get("confidence") == 0.0:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ---------------------------------------------------------------------------
# Settings / Provider Configuration Endpoints
# ---------------------------------------------------------------------------

@app.get("/config/providers", summary="List All AI Providers")
def list_providers():
    """
    Return all available AI providers with their configuration status and which is currently active.
    """
    return {
        "providers": provider_config.list_providers(),
        "active_provider": provider_config.active,
    }

@app.post("/config/providers/active", summary="Switch Active AI Provider")
def set_active_provider(request: SetProviderRequest):
    """
    Switch the active AI provider used for clinical report analysis.
    Accepted values: gemini_primary, gemini_fallback, groq
    """
    try:
        provider_config.active = request.provider_id
        cfg = provider_config.get_config()
        return {
            "success": True,
            "message": f"Active provider switched to '{cfg['label']}'.",
            "active_provider": provider_config.active,
            "provider_details": cfg,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
