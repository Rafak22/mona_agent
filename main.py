import logging
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.conversation_logger import to_uuid, get_or_create_conversation, log_turn_via_rpc
from onboarding_graph import start_onboarding, resume_onboarding
from agent import run_agent, answer_with_openai, route_query
from tools.supabase_client import supabase
from dotenv import load_dotenv
from typing import List, Dict, Optional
import asyncio
import openai  # for catching SDK-specific exceptions across versions
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

def _fetch_profile_from_db(user_uuid_str: str) -> Optional[Dict[str, str]]:
    if not _sb:
        return None
    try:
        res = _sb.table("profiles").select("user_role,industry,company_size,website_status,website_url,primary_goals,budget_range") \
            .eq("user_id", user_uuid_str).limit(1).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logging.info(f"[chat] fetch profile failed: {e}")
    return None

app = FastAPI()

# Expanded CORS to support Lovable subdomains and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\.)*(lovable\.app|lovable\.dev|lovableproject\.com|railway\.app)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{path:path}")
def cors_preflight(path: str, request: Request) -> Response:
    origin = request.headers.get("origin") or ""
    acrm = request.headers.get("access-control-request-method") or ""
    acrh = request.headers.get("access-control-request-headers") or ""
    logging.info(f"[preflight] path=/{path} origin={origin} method={acrm} headers={acrh}")
    return Response(status_code=204)

# Simple classifiers to detect questions vs onboarding intent
def _is_question(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return False
    if ("?" in t) or ("؟" in t) or t.endswith("?") or t.endswith("؟"):
        return True
    q_starts = (
        "ما", "ماهي", "متى", "كيف", "ليش", "لماذا", "هل", "كم", "وين", "أين", "وش", "ايش",
        "what", "how", "why", "when", "where", "who", "which", "can", "should"
    )
    return any(t.startswith(s) for s in q_starts)

def _wants_onboarding(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True
    triggers = ("ابدأ", "ابدا", "بدء", "تعريف", "سجل", "onboard", "onboarding", "start")
    return any(x in t for x in triggers)

@app.get("/")
def read_root():
    return {"message": "👋 MORVO is ready to analyze Almarai data!"}

class OBStartReq(BaseModel):
    user_id: str

class OBStepReq(BaseModel):
    user_id: str
    value: str

class OpenAIChatRequest(BaseModel):
    prompt: str
    system: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None

class ResetRequest(BaseModel):
    user_id: str
    mode: Optional[str] = "conversation"  # "conversation" | "all"

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
def chat_with_mona(user_input: UserMessage, request: Request):
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

    # If user greets, profile isn't complete, or there is no profile row in Supabase, choose between onboarding or answering directly
    greeting_triggers = [
        "",
        "hi",
        "hello",
        "ابدأ",
        "start",
        "مورفو",
        "اهلا",
        "أهلا",
        "مرحبا",
    ]
    # Check if a profile row exists in Supabase for this user (persistent, not just in-memory)
    profile_exists = False
    if _sb:
        try:
            uid = str(user_uuid)
            res = _sb.table("profiles").select("user_id").eq("user_id", uid).limit(1).execute()
            profile_exists = bool(res.data)
        except Exception as e:
            logging.info(f"[chat] profile_exists check skipped: {e}")

    needs_onboarding = (profile.state != UserProfileState.COMPLETE) or (not profile_exists)
    is_greeting = message.lower() in greeting_triggers
    wants_onb = _wants_onboarding(message)
    is_q = _is_question(message)

    # Strict onboarding-first mode for new users (frontend handles the flow)
    if not profile_exists and not wants_onb:
        reply = (
            "مرحباً بك في مورفو! قبل ما نبدأ بالإجابات، خلّينا نجهّز ملفك التسويقي بسرعة. "
            "اضغط على زر البدء في الواجهة أو أرسل كلمة: ابدأ"
        )
        save_message_to_db(user_input.user_id, "user", message)
        save_message_to_db(user_input.user_id, "assistant", reply)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding_required", "assistant", reply)
        return {"reply": reply}

    if needs_onboarding and (is_greeting or wants_onb) and not is_q:
        WELCOME_TEXT = (
            "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق. أساعدك في تحليل السمعة والمنشورات وSEO،"
            " ونبني خطط تحقق عائد واضح. خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
        )
        # If onboarding not started in this session, start; otherwise resume with provided message
        if profile.state == UserProfileState.COMPLETE:
            # Start flow
            ob = start_onboarding(user_input.user_id)
            # mark as in-progress
            profile.state = UserProfileState.ASK_NAMEimage.png 
            update_user_profile(user_input.user_id, profile)
            ui = ob.get("ui") or {}
            reply = ui.get("message") or WELCOME_TEXT
            if not reply:
                reply = WELCOME_TEXT
        else:
            # Resume flow with the user's message
            step = resume_onboarding(user_input.user_id, message)
            if step.get("done"):
                profile.state = UserProfileState.COMPLETE
                update_user_profile(user_input.user_id, profile)
                reply = "تم حفظ بياناتك ✅ كيف أقدر أساعدك اليوم؟"
            else:
                ui = step.get("ui") or {}
                reply = ui.get("message") or WELCOME_TEXT
                if not reply:
                    reply = WELCOME_TEXT

        # Save messages
        save_message_to_db(user_input.user_id, "user", message)
        save_message_to_db(user_input.user_id, "assistant", reply)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding", "user", message)
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding", "assistant", reply)
        logging.info(f"[chat:onboarding] origin={request.headers.get('origin','')} user_id={user_input.user_id} msg={message[:60]} reply={(reply or '')[:60]}...")
        return {"reply": reply}
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

    # If profile exists and is complete, greet returning user once
    if profile.state == UserProfileState.COMPLETE and profile_exists and message.lower() in greeting_triggers:
        db_prof = _fetch_profile_from_db(str(user_uuid))
        name_hint = "ضيفنا الكريم"  # fallback
        if db_prof and isinstance(db_prof.get("primary_goals"), list) and db_prof.get("primary_goals"):
            name_hint = "ضيفنا الكريم"
        reply = "أهلاً برجعتك! أنا MORVO 🤝 جاهز أساعدك. وش حاب نبدأ فيه اليوم؟"
        save_message_to_db(user_input.user_id, "user", message)
        save_message_to_db(user_input.user_id, "assistant", reply)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "welcome_back", "assistant", reply)
        return {"reply": reply}

    # Get conversation history from Supabase
    history = get_conversation_history(user_input.user_id)
    
    # Route: try Java endpoints first; otherwise call OpenAI directly (no DB dependency)
    origin = request.headers.get("origin") or ""
    logging.info(f"[chat] received origin={origin} user_id={user_input.user_id} msg={message[:80]}...")

    try:
        java_response = route_query(message)
        if java_response:
            response = java_response
        else:
            # Fallback to OpenAI directly with conversation history
            from agent import MORVO_SYSTEM_PROMPT
            response = answer_with_openai(message, system_text=MORVO_SYSTEM_PROMPT, history=history)
        if needs_onboarding and not (is_greeting or wants_onb):
            response = (response or "").strip() + "\n\nملاحظة: ما تعرّفنا عليك بعد. إذا حاب نجهّز التجربة حسب نشاطك، اكتب: ابدأ"
    except Exception as e:  # Map specific OpenAI-related errors to clearer HTTP codes/messages
        # Normalize OpenAI exception classes across SDK versions
        oai_error_mod = getattr(openai, "error", None)
        AuthErr = getattr(openai, "AuthenticationError", None) or (getattr(oai_error_mod, "AuthenticationError", None) if oai_error_mod else None)
        RateErr = getattr(openai, "RateLimitError", None) or (getattr(oai_error_mod, "RateLimitError", None) if oai_error_mod else None)
        TimeoutErr = getattr(openai, "APITimeoutError", None)

        if isinstance(e, (TimeoutError, asyncio.TimeoutError)) or (TimeoutErr and isinstance(e, TimeoutErr)):
            raise HTTPException(status_code=504, detail="OpenAI request timed out.")
        if (AuthErr and isinstance(e, AuthErr)):
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        if (RateErr and isinstance(e, RateErr)):
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded.")
        # Any other unexpected exception → return 502 including the exception message for debugging
        raise HTTPException(status_code=502, detail=f"OpenAI error: {e}")

    # Save messages to Supabase messages table
    save_message_to_db(user_input.user_id, "user", message)
    save_message_to_db(user_input.user_id, "assistant", response)

    # Log both user and assistant turns with minimal state patch
    if conversation_id:
        log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "chat", "user", message)
        log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "chat", "assistant", response)

    logging.info(f"[chat] origin={origin} user_id={user_input.user_id} msg={message[:60]} reply={(response or '')[:60]}...")
    return {"reply": response}

@app.get("/profile/status")
def profile_status(user_id: str):
    try:
        uid = str(to_uuid(user_id))
        if _sb:
            res = _sb.table("profiles").select("user_id").eq("user_id", uid).limit(1).execute()
            return {"has_profile": bool(res.data)}
        return {"has_profile": False}
    except Exception as e:
        logging.info(f"[profile_status] error: {e}")
        return {"has_profile": False}

@app.post("/onboarding/start_compat")
def onboarding_start_compat(event: OBStartReq):
    res = onboarding_start(event)
    ui = res.get("ui") or {}
    msg = ui.get("message") or ""
    if not msg:
        msg = (
            "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق. أساعدك في تحليل السمعة والمنشورات وSEO،"
            " ونبني خطط تحقق عائد واضح. خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
        )
    logging.info(f"[onboarding_start_compat] user_id={event.user_id} reply_len={len(msg)}")
    return {"reply": msg}

@app.post("/onboarding/step_compat")
def onboarding_step_compat(event: OBStepReq):
    res = onboarding_step(event)
    if res.get("done"):
        msg_done = "تم حفظ بياناتك ✅ اسألني أي سؤال تسويقي الآن."
        logging.info(f"[onboarding_step_compat] done user_id={event.user_id}")
        return {"reply": msg_done}
    ui = res.get("ui") or {}
    msg = ui.get("message") or ""
    if not msg:
        msg = (
            "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق. أساعدك في تحليل السمعة والمنشورات وSEO،"
            " ونبني خطط تحقق عائد واضح. خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
        )
    logging.info(f"[onboarding_step_compat] user_id={event.user_id} reply_len={len(msg)}")
    return {"reply": msg}

@app.get("/diag")
def diag():
    # Try a lightweight OpenAI call without Lovable to isolate issues
    chat_test: str
    try:
        chat_test = answer_with_openai("ping", system_text="diag", history=[])
    except Exception as e:
        chat_test = f"error: {e}"
    return {
        "has_supabase": bool(_sb),
        "endpoints": [
            "onboarding/start",
            "onboarding/step",
            "onboarding/start_compat",
            "onboarding/step_compat",
            "chat",
        ],
        "chat_test": chat_test,
    }

@app.post("/openai/chat")
def openai_chat(req: OpenAIChatRequest):
    try:
        system_text = req.system or "You are MORVO, a helpful marketing assistant."
        resp = answer_with_openai(req.prompt, system_text=system_text, history=req.history)
        return {"reply": resp}
    except Exception as e:
        oai_error_mod = getattr(openai, "error", None)
        AuthErr = getattr(openai, "AuthenticationError", None) or (getattr(oai_error_mod, "AuthenticationError", None) if oai_error_mod else None)
        RateErr = getattr(openai, "RateLimitError", None) or (getattr(oai_error_mod, "RateLimitError", None) if oai_error_mod else None)
        TimeoutErr = getattr(openai, "APITimeoutError", None)

        if isinstance(e, (TimeoutError, asyncio.TimeoutError)) or (TimeoutErr and isinstance(e, TimeoutErr)):
            raise HTTPException(status_code=504, detail="OpenAI request timed out.")
        if (AuthErr and isinstance(e, AuthErr)):
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        if (RateErr and isinstance(e, RateErr)):
            raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded.")
        raise HTTPException(status_code=502, detail=f"OpenAI error: {e}")

@app.post("/reset")
def reset(req: ResetRequest):
    # Clear conversation history always
    cleared = clear_conversation_history(req.user_id)
    # Optionally clear profile row and in-memory state
    if req.mode == "all":
        try:
            users[req.user_id] = UserProfile()  # reset in-memory
            if _sb:
                uid = str(to_uuid(req.user_id))
                _sb.table("profiles").delete().eq("user_id", uid).execute()
        except Exception as e:
            logging.info(f"[reset] profile clear skipped: {e}")
    return {"cleared": bool(cleared), "mode": req.mode}