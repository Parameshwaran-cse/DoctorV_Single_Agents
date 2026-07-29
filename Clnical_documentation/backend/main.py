import time
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel
import os

import models
from database import engine, get_db
import auth
from schemas import DocumentationRequest, UserCreate, Token
from agent import medical_documentation_agent, PROVIDER_RUNNERS

# Ensure env vars are loaded early
load_dotenv()

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medical Documentation Web App",
    description="Full-stack AI Agent backend API.",
    version="2.0.0"
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Documentation Agent API is running"}

@app.post("/auth/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/generate", response_class=JSONResponse)
def generate_documentation(request: DocumentationRequest, current_user: models.User = Depends(auth.get_current_user)):
    """
    Generate structured medical documentation based on patient clinical data.
    """
    start_time = time.perf_counter()
    
    try:
        # Run the agent (synchronous call using genai client)
        result = medical_documentation_agent.run(request)
        
        execution_time = round(time.perf_counter() - start_time, 3)
        
        if "error" in result:
            # If the fallback error dictionary is returned
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": result["error"],
                    "details": result.get("details", "Unknown error")
                }
            )
            
        return {
            "status": "success",
            "execution_time_seconds": execution_time,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = round(time.perf_counter() - start_time, 3)
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "An unexpected error occurred during documentation generation.",
                "details": str(e),
                "execution_time_seconds": execution_time
            }
        )

# ─── Settings: AI Provider ────────────────────────────────────────────────────

class ProviderUpdate(BaseModel):
    provider: str

@app.get("/settings/providers")
def list_providers(current_user: models.User = Depends(auth.get_current_user)):
    """Return all available AI providers and the currently active one."""
    providers = [
        {"id": "gemini", "name": "Google Gemini",  "model": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),        "color": "#4285F4"},
        {"id": "openai", "name": "OpenAI GPT",      "model": os.environ.get("OPENAI_MODEL",  "gpt-4o"),                "color": "#10a37f"},
        {"id": "groq",   "name": "Groq",            "model": os.environ.get("GROQ_MODEL",   "llama-3.3-70b-versatile"),"color": "#f55036"},
    ]
    return {
        "active_provider": medical_documentation_agent.get_active_provider(),
        "providers": providers,
    }

@app.post("/settings/provider")
def set_provider(body: ProviderUpdate, current_user: models.User = Depends(auth.get_current_user)):
    """Switch the active AI provider."""
    try:
        medical_documentation_agent.set_active_provider(body.provider)
        return {"status": "ok", "active_provider": body.provider}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
