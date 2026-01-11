import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(url, key)

def save_log(content: str, category: str, severity: str, reasoning_chain: list, suggested_action: str):
    data = {
        "content": content,
        "category": category,
        "severity": severity,
        "reasoning_chain": reasoning_chain,
        "suggested_action": suggested_action
    }
    try:
        response = supabase.table("harassment_logs").insert(data).execute()
        return response
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        return None

def fetch_history(limit: int = 20):
    try:
        response = supabase.table("harassment_logs").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []
