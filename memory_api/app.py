from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time
import os
from store import MemoryStore

app = FastAPI(title="Memory API", version="1.0.0")

# Initialize memory store
db_path = os.getenv("MEM_DB", "mem.db")
memory_store = MemoryStore(db_path)

class RecallRequest(BaseModel):
    user_id: str
    query: str
    k: int = 5
    context_window: int = 12

class RecallResponse(BaseModel):
    memories: List[dict]
    usage: dict

class RememberRequest(BaseModel):
    user_id: str
    text: str
    tags: List[str] = []

class RememberResponse(BaseModel):
    ok: bool

class SearchDocRequest(BaseModel):
    user_id: str
    query: str
    k: int = 5
    context_window: int = 12

class SearchDocResponse(BaseModel):
    chunks: List[dict]

@app.get("/healthz")
async def health_check():
    return {"ok": True}

@app.post("/recall", response_model=RecallResponse)
async def recall_memories(request: RecallRequest):
    start_time = time.time()
    
    try:
        memories = memory_store.recall_memories(request.user_id, request.k)
        latency_ms = int((time.time() - start_time) * 1000)
        
        return RecallResponse(
            memories=memories,
            usage={"latency_ms": latency_ms}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory recall failed: {str(e)}")

@app.post("/remember", response_model=RememberResponse)
async def remember_text(request: RememberRequest):
    try:
        memory_store.add_memory(request.user_id, request.text, request.tags)
        return RememberResponse(ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory storage failed: {str(e)}")

@app.post("/search_doc", response_model=SearchDocResponse)
async def search_documents(request: SearchDocRequest):
    # Stub implementation - to be replaced with FAISS later
    return SearchDocResponse(chunks=[])
