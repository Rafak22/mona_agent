from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from supabase import create_client, Client

app = FastAPI(title="Supabase Proxy", version="1.0.0")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

supabase: Client = create_client(supabase_url, supabase_key)

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    lang: Optional[str] = None
    title: Optional[str] = None
    state: Optional[str] = None

class ProfileResponse(BaseModel):
    user_id: str
    name: Optional[str] = None
    role: Optional[str] = None
    goal: Optional[str] = None
    lang: Optional[str] = None
    title: Optional[str] = None
    state: Optional[str] = None

class UpdateResponse(BaseModel):
    ok: bool

@app.get("/healthz")
async def health_check():
    return {"ok": True}

@app.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str):
    try:
        response = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile_data = response.data[0]
        return ProfileResponse(
            user_id=profile_data.get("user_id", user_id),
            name=profile_data.get("name"),
            role=profile_data.get("role"),
            goal=profile_data.get("goal"),
            lang=profile_data.get("lang"),
            title=profile_data.get("title"),
            state=profile_data.get("state")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@app.patch("/profiles/{user_id}", response_model=UpdateResponse)
async def update_profile(user_id: str, profile_update: ProfileUpdate):
    try:
        # Prepare update data
        update_data = profile_update.dict(exclude_unset=True)
        update_data["user_id"] = user_id
        
        # Upsert the profile
        response = supabase.table("profiles").upsert(update_data).execute()
        
        if response.data:
            return UpdateResponse(ok=True)
        else:
            raise HTTPException(status_code=500, detail="Failed to update profile")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")
