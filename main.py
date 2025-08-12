# main.py
import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Chat plumbing lives in agent.py
from agent import route_query, answer_with_openai, get_profile, build_system_prompt

# ---- Supabase client (v2) ----
try:
    from supabase import create_client  # pip install supabase
except Exception as e:
    create_client = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Prefer service key on the backend; anon works if your RLS allows it
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

_sb = create_client(SUPABASE_URL, SUPABASE_KEY) if (create_client and SUPABASE_URL and SUPABASE_KEY) else None

app = FastAPI()


# ---------- MODELS ----------
class ProfileUpsert(BaseModel):
    # EXACT schema you shared
    user_id: str
    user_role: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website_status: Optional[str] = None   # "Yes"/"No"
    website_url: Optional[str] = None
    primary_goals: List[str] = []          # default to []
    budget_range: Optional[str] = None


class ChatReq(BaseModel):
    user_id: str
    message: str

# (optional) simple system prompt; you can enrich it from Supabase profile if you already wired that
def _system_prompt() -> str:
    return (
        "أنت MORVO، مستشارة تسويق ثنائية اللغة (عربي/إنجليزي). "
        "قدّمي إجابات عملية ومختصرة وركزي على العائد."
    )

# ---------- ENDPOINTS ----------
@app.post("/profile/upsert")
def upsert_profile(p: ProfileUpsert):
    """
    Upserts the user's onboarding/journey info into the 'profiles' table.
    Columns: user_id, user_role, industry, company_size, website_status,
             website_url, primary_goals, budget_range
    """
    if not _sb:
        raise HTTPException(status_code=500, detail="Supabase client not configured")

    payload = p.model_dump(exclude_none=True)  # don't send None columns
    try:
        res = _sb.table("profiles").upsert(payload, on_conflict="user_id").execute()
        data = getattr(res, "data", None) or []
        return {"ok": True, "profile": (data[0] if data else payload)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upsert failed: {e}")


@app.get("/profile/{user_id}")
def get_profile_api(user_id: str):
    """Optional helper to fetch the stored profile for debugging."""
    prof = get_profile(user_id)
    return {"ok": True, "profile": prof}


@app.post("/chat")
def chat(req: ChatReq):
    # 1) Try Java routes – only if we got a REAL non-empty answer
    routed = route_query(req.message)
    if isinstance(routed, str) and routed.strip():
        return {"reply": routed}

    # 2) Fall back to OpenAI
    try:
        reply = answer_with_openai(req.message, system_text=_system_prompt())
        return {"reply": reply}
    except Exception as e:
        # Return JSON error instead of letting the browser show "Failed to fetch"
        raise HTTPException(status_code=502, detail=f"LLM provider error: {e}")


# ---- Optional: previously used Perplexity route should be removed/disabled ----
# @app.post("/360prep")
# def deprecated_360():
#     return {"error": "Perplexity integration removed. Use /chat instead."}