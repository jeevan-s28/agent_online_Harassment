from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from database import fetch_history

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "https://agent-8om44jaoe-jeevan-ss-projects-98df6ea7.vercel.app",
    "https://agent-online-harassment.vercel.app", # Adding main domain if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str



router = APIRouter(prefix="/api")

@app.get("/")
def read_root():
    return {"status": "active", "service": "Harassment Detection API"}

@router.post("/analyze")
async def analyze_text(request: AnalyzeRequest):
    from agent_graph import app_graph
    
    initial_state = {"input_text": request.text}
    result = app_graph.invoke(initial_state)
    
    return {
        "status": "harmful" if result["policy_violations"] else "safe",
        "category": result["policy_violations"][0] if result["policy_violations"] else "None",
        "severity": result["severity_score"],
        "reasoning_chain": result["reasoning_history"],
        "suggested_action": result["final_decision"]
    }



@router.get("/history")
async def get_history():
    return fetch_history()

app.include_router(router)
