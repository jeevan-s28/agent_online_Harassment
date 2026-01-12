from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from database import fetch_history

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str

class ImportRequest(BaseModel):
    url: str

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

@router.post("/import-instagram")
async def import_instagram(request: ImportRequest):
    import instaloader
    from agent_graph import app_graph
    
    L = instaloader.Instaloader()
    
    # Login if credentials are provided
    insta_user = os.environ.get("INSTAGRAM_USER")
    insta_pass = os.environ.get("INSTAGRAM_PASSWORD")
    
    login_success = False
    if insta_user and insta_pass:
        try:
            L.login(insta_user, insta_pass)
            login_success = True
        except Exception as e:
            print(f"Warning: Instagram Login Failed: {str(e)}")
            # Continue anonymously
    
    if not login_success:
         # Try to load session if available
        try:
            L.load_session_from_file(insta_user) if insta_user else None
        except:
            pass
    
    # Extract shortcode from URL (supports /p/ and /reel/)
    shortcode = None
    if "/p/" in request.url:
        shortcode = request.url.split("/p/")[1].split("/")[0]
    elif "/reel/" in request.url:
        shortcode = request.url.split("/reel/")[1].split("/")[0]
    
    if not shortcode:
        return {"status": "error", "message": "Invalid Instagram URL. Must contain /p/ or /reel/"}
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        comments = []
        for comment in post.get_comments():
            comments.append(comment.text)
            if len(comments) >= 7:  # Limit to 7 for demo speed
                break
        
        results = []
        for text in comments:
            initial_state = {"input_text": text, "source": "Instagram"}
            res = app_graph.invoke(initial_state)
            results.append({
                "text": text,
                "status": "harmful" if res["policy_violations"] else "safe",
                "category": res["policy_violations"][0] if res["policy_violations"] else "None",
                "severity": res["severity_score"]
            })
            
        return {"status": "success", "imported_count": len(results), "results": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/history")
async def get_history():
    return fetch_history()

app.include_router(router)
