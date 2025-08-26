from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Dict, Any, Optional
from onboarding import handle_onboarding

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    step: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Get service URLs from environment
    memory_api_base = os.getenv("MEMORY_API_BASE", "http://localhost:8000")
    supabase_api_base = os.getenv("SUPABASE_API_BASE", "http://localhost:8001")
    
    # First, check onboarding gate
    onboarding_result = await handle_onboarding(
        request.user_id, 
        request.message, 
        supabase_api_base
    )
    
    if onboarding_result:
        # Still in onboarding - short-circuit and return onboarding response
        # Log onboarding progress to memory
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                await client.post(f"{memory_api_base}/remember", json={
                    "user_id": request.user_id,
                    "text": f"onboarding_progress:{onboarding_result['step']}",
                    "tags": ["onboarding"]
                })
            except Exception as e:
                print(f"Failed to log onboarding progress: {e}")
        
        return ChatResponse(
            reply=onboarding_result["reply"],
            step=onboarding_result["step"]
        )
    
    # Onboarding complete - proceed with normal chat flow
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Recall memories
            memory_response = await client.post(f"{memory_api_base}/recall", json={
                "user_id": request.user_id,
                "query": request.message,
                "k": 5,
                "context_window": 12
            })
            memory_response.raise_for_status()
            memories_data = memory_response.json()
            memories = memories_data.get("memories", [])
            
            # Log the query to memory
            await client.post(f"{memory_api_base}/remember", json={
                "user_id": request.user_id,
                "text": f"last_query:{request.message}",
                "tags": ["trace"]
            })
            
            # Compose simple reply
            memory_count = len(memories)
            reply = f"تم—لقيت {memory_count} ذكرى..."
            
            # Add some context from memories if available
            if memories:
                latest_memory = memories[0]
                reply += f"\n\nآخر ذكرى: {latest_memory['text'][:100]}..."
            
            return ChatResponse(reply=reply)
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Memory API error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat processing error: {e}")
