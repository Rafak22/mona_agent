import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.perplexity_tool import fetch_perplexity_insight as fetch_ai_insight
from tools.conversation_logger import to_uuid, get_or_create_conversation, log_turn_via_rpc
from onboarding_graph import start_onboarding, resume_onboarding
from agent import run_agent, answer_with_openai
from tools.supabase_client import supabase
from dotenv import load_dotenv
from typing import List, Dict, Optional
import os

# Load .env and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client
_sb = supabase if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY") else None

def clear_conversation_history(user_id: str) -> bool:
    """Clear conversation history for a user when they start over"""
    if not _sb:
        return False
    
    try:
        _sb.table("messages").delete().eq("user_id", user_id).execute()
        return True
    except Exception as e:
        logging.error(f"Error clearing conversation history: {e}")
        return False

def get_conversation_history(user_id: str) -> List[Dict[str, str]]:
    """Retrieve conversation history from Supabase messages table"""
    if not _sb:
        return []
    
    try:
        result = _sb.table("messages").select("role, content").eq("user_id", user_id).order("created_at", desc=False).execute()
        if result.data:
            return [{"role": msg["role"], "content": msg["content"]} for msg in result.data]
        return []
    except Exception as e:
        logging.error(f"Error fetching conversation history: {e}")
        return []

def save_message_to_db(user_id: str, role: str, content: str) -> bool:
    """Save a message to the Supabase messages table"""
    if not _sb:
        return False
    
    try:
        _sb.table("messages").insert({
            "user_id": user_id,
            "role": role,
            "content": content
        }).execute()
        return True
    except Exception as e:
        logging.error(f"Error saving message to DB: {e}")
        return False

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://58f42318-2170-4cd0-8a86-1dcb3c26f3ea.lovableproject.com",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "👋 MORVO is ready to analyze Almarai data!"}

class OBStartReq(BaseModel):
    user_id: str

class OBStepReq(BaseModel):
    user_id: str
    value: str

@app.post("/onboarding/start")
def onboarding_start(event: OBStartReq):
    result = start_onboarding(event.user_id)
    ui = result.get("ui", {}) or {}
    # normalize shape expected by FE
    payload = {
        "conversation_id": result.get("conversation_id"),
        "done": result.get("done", False),
        "ui_type": ui.get("ui_type"),
        "message": ui.get("message"),
        "options": ui.get("options", []),
        "fields": ui.get("fields", []),
        "state_updates": ui.get("state_updates", {}),
    }
    return payload

@app.post("/onboarding/step")
def onboarding_step(event: OBStepReq):
    if not event.user_id:
        return {"ui_type": "input", "message": "أدخل معرف المستخدم", "fields": [{"id": "user_id", "label": "User ID"}], "state_updates": {}}
    result = resume_onboarding(event.user_id, event.value)
    ui = result.get("ui", {}) or {}
    payload = {
        "conversation_id": result.get("conversation_id"),
        "done": result.get("done", False),
        "ui_type": ui.get("ui_type"),
        "message": ui.get("message"),
        "options": ui.get("options", []),
        "fields": ui.get("fields", []),
        "state_updates": ui.get("state_updates", {}),
    }
    return payload

@app.post("/chat")
def chat_with_mona(user_input: UserMessage):
    if not user_input.user_id:
        return {
            "reply": "مرحباً! أنا مورفو، وكيلتك التسويقية الذكية. جاهزة لتحليل بيانات المراعي — من وين تحب نبدأ اليوم؟"
        }

    profile = get_user_profile(user_input.user_id)
    message = user_input.message.strip()

    # Ensure conversation exists
    user_uuid = to_uuid(user_input.user_id)
    conversation_id = get_or_create_conversation(user_uuid)

    if message == "start over":
        profile.state = UserProfileState.CONFIRM_RESET
        update_user_profile(user_input.user_id, profile)
        # Save user message to DB
        save_message_to_db(user_input.user_id, "user", message)
        # log user turn
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "confirm_reset", "user", message)
        return {"reply": "⚠️ هل أنت متأكد أنك تريد البدء من جديد؟ اكتب: نعم"}

    if profile.state == UserProfileState.CONFIRM_RESET:
        if message == "نعم":
            users[user_input.user_id] = UserProfile()
            if user_input.user_id in user_memory:
                del user_memory[user_input.user_id]
            # Clear conversation history from database
            clear_conversation_history(user_input.user_id)
            # Save user message to DB
            save_message_to_db(user_input.user_id, "user", message)
            reply = "🔄 تم إعادة تعيين المحادثة. أهلاً من جديد! ما اسمك؟"
            # Save assistant reply to DB
            save_message_to_db(user_input.user_id, "assistant", reply)
            # log
            if conversation_id:
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "reset", "user", message)
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "reset", "assistant", reply)
            return {"reply": reply}
        else:
            profile.state = UserProfileState.COMPLETE
            update_user_profile(user_input.user_id, profile)
            # Save user message to DB
            save_message_to_db(user_input.user_id, "user", message)
            reply = "❌ تم إلغاء إعادة التهيئة. نكمل من وين وقفنا 😊"
            # Save assistant reply to DB
            save_message_to_db(user_input.user_id, "assistant", reply)
            if conversation_id:
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "cancel_reset", "user", message)
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "cancel_reset", "assistant", reply)
            return {"reply": reply}

    if profile.state == UserProfileState.COMPLETE and message.lower() in ["", "hi", "hello", "ابدأ", "start", "مورفو"]:
        # Save user message to DB
        save_message_to_db(user_input.user_id, "user", message)
        reply = (
            "أهلاً! أنا **MORVO** — وكيلتك التسويقية الذكية المتخصصة في تحليل بيانات المراعي.\n\n"
            "🔍 أقدر أساعدك في:\n"
            "• تحليل ذكر العلامة التجارية وسمعتها\n"
            "• متابعة أداء المنشورات على وسائل التواصل\n"
            "• تحليل أداء SEO والكلمات المفتاحية\n\n"
            "💡 من وين تحب نبدأ اليوم؟"
        )
        # Save assistant reply to DB
        save_message_to_db(user_input.user_id, "assistant", reply)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "greeting", "user", message)
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "greeting", "assistant", reply)
        return {"reply": reply}

    # Get conversation history from Supabase
    history = get_conversation_history(user_input.user_id)
    
    # Route through simplified agent with conversation history
    response = run_agent(user_input.user_id, message, profile, history)

    # Save messages to Supabase messages table
    save_message_to_db(user_input.user_id, "user", message)
    save_message_to_db(user_input.user_id, "assistant", response)

    # Log both user and assistant turns with minimal state patch
    if conversation_id:
        log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "chat", "user", message)
        log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "chat", "assistant", response)

    return {"reply": response}

# 360° feature (unchanged)
class CompanyRequest(BaseModel):
    company_name: str
    user_id: str

@app.post("/360prep")
def generate_360_report(req: CompanyRequest):
    intro = "📊 360° Snapshot of Almarai by MORVO:\n\n"
    prompt = f"""Give a short marketing snapshot for Almarai.

Include:
- Brand Mentions & Reputation
- Social Media Performance
- SEO & Keywords Analysis

Keep it short, 40–100 words, bullet format, good for fast scan.
"""
    response = fetch_ai_insight.invoke(intro + prompt)
    return {"reply": response}