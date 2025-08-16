import streamlit as st
import logging
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
import openai
import asyncio
import re

# Import your existing modules
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.conversation_logger import to_uuid, get_or_create_conversation, log_turn_via_rpc
from onboarding_graph import start_onboarding, resume_onboarding
from agent import run_agent, answer_with_openai, route_query, MORVO_SYSTEM_PROMPT
from tools.supabase_client import supabase

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client
_sb = supabase if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY") else None

# Page configuration
st.set_page_config(
    page_title="مورفو - مساعدك الذكي في التسويق",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for RTL and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    .main {
        direction: rtl;
        font-family: 'Cairo', sans-serif;
    }
    
    .stTextInput > div > div > input {
        direction: rtl;
        text-align: right;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    
    .welcome-card {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Helper functions from main.py
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

# Intent detection functions
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

def _looks_like_name(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    low = t.lower()
    _NON_NAMES = {"ايه","أيه","ايوه","أيوه","نعم","لا","تمام","طيب","اوكي","أوكي","اوكيه","مرحبا","اهلا","أهلا","هلا","ok","okay","thanks","thank you"}
    if low in _NON_NAMES:
        return False
    _AR = re.compile(r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s\-']{2,40}$")
    _LAT = re.compile(r"^[A-Za-z\s\-']{2,40}$")
    return bool(_AR.match(t) or _LAT.match(t))

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'onboarding_state' not in st.session_state:
    st.session_state.onboarding_state = None
if 'profile_complete' not in st.session_state:
    st.session_state.profile_complete = False

def generate_user_id():
    """Generate a unique user ID for the session"""
    import uuid
    return str(uuid.uuid4())

def chat_with_mona(message: str, user_id: str):
    """Main chat function adapted from main.py"""
    if not user_id:
        return "مرحباً! أنا مورفو، وكيلتك التسويقية الذكية. جاهزة لتحليل بيانات المراعي — من وين تحب نبدأ اليوم؟"

    profile = get_user_profile(user_id)
    message = message.strip()

    # Ensure conversation exists
    user_uuid = to_uuid(user_id)
    conversation_id = get_or_create_conversation(user_uuid)

    if message == "start over":
        profile.state = UserProfileState.CONFIRM_RESET
        update_user_profile(user_id, profile)
        save_message_to_db(user_id, "user", message)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "confirm_reset", "user", message)
        return "⚠️ هل أنت متأكد أنك تريد البدء من جديد؟ اكتب: نعم"

    if profile.state == UserProfileState.CONFIRM_RESET:
        if message == "نعم":
            users[user_id] = UserProfile()
            if user_id in user_memory:
                del user_memory[user_id]
            clear_conversation_history(user_id)
            save_message_to_db(user_id, "user", message)
            reply = "🔄 تم إعادة تعيين المحادثة. أهلاً من جديد! ما اسمك؟"
            save_message_to_db(user_id, "assistant", reply)
            if conversation_id:
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "reset", "user", message)
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "reset", "assistant", reply)
            return reply
        else:
            profile.state = UserProfileState.COMPLETE
            update_user_profile(user_id, profile)
            save_message_to_db(user_id, "user", message)
            reply = "❌ تم إلغاء إعادة التهيئة. نكمل من وين وقفنا 😊"
            save_message_to_db(user_id, "assistant", reply)
            if conversation_id:
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "cancel_reset", "user", message)
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "cancel_reset", "assistant", reply)
            return reply

    # Check if profile exists in database
    profile_exists = False
    if _sb:
        try:
            uid = str(user_uuid)
            res = _sb.table("profiles").select("user_id").eq("user_id", uid).limit(1).execute()
            profile_exists = bool(res.data)
        except Exception as e:
            logging.info(f"[chat] profile_exists check skipped: {e}")

    # Handle onboarding for new users
    if not profile_exists:
        wants_onb = _wants_onboarding(message)
        is_greeting = message.lower() in ["", "hi", "hello", "ابدأ", "start", "مورفو", "اهلا", "أهلا", "مرحبا"]
        
        if wants_onb or is_greeting:
            if profile.state == UserProfileState.COMPLETE:
                ob = start_onboarding(user_id)
                profile.state = UserProfileState.IN_ONBOARDING
                update_user_profile(user_id, profile)
                ui = ob.get("ui") or {}
                reply = ui.get("message") or "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق. خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
            else:
                step = resume_onboarding(user_id, message)
                if step.get("done"):
                    profile.state = UserProfileState.COMPLETE
                    update_user_profile(user_id, profile)
                    reply = "تم حفظ بياناتك ✅ كيف أقدر أساعدك اليوم؟"
                else:
                    ui = step.get("ui") or {}
                    reply = ui.get("message") or "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق. خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
            
            save_message_to_db(user_id, "user", message)
            save_message_to_db(user_id, "assistant", reply)
            if conversation_id:
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding", "user", message)
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding", "assistant", reply)
            return reply
        else:
            reply = (
                "مرحباً بك في مورفو! أنا مستشارتك الذكية للتسويق. 🚀\n\n"
                "🔍 أقدر أساعدك في:\n"
                "• تحليل ذكر العلامة التجارية وسمعتها\n"
                "• متابعة أداء المنشورات على وسائل التواصل\n"
                "• تحليل أداء SEO والكلمات المفتاحية\n\n"
                "💡 من وين تحب نبدأ اليوم؟ أو اكتب 'ابدأ' لتجهيز ملفك التسويقي."
            )
            save_message_to_db(user_id, "user", message)
            save_message_to_db(user_id, "assistant", reply)
            if conversation_id:
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "welcome", "user", message)
                log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "welcome", "assistant", reply)
            return reply
    
    # Handle ongoing onboarding
    elif profile.state == UserProfileState.IN_ONBOARDING:
        step = resume_onboarding(user_id, message)
        if step.get("done"):
            profile.state = UserProfileState.COMPLETE
            update_user_profile(user_id, profile)
            reply = "تم حفظ بياناتك ✅ كيف أقدر أساعدك اليوم؟"
        else:
            ui = step.get("ui") or {}
            reply = ui.get("message") or "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق. خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
        
        save_message_to_db(user_id, "user", message)
        save_message_to_db(user_id, "assistant", reply)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding", "user", message)
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "onboarding", "assistant", reply)
        return reply

    # Handle returning users
    greeting_triggers = ["", "hi", "hello", "ابدأ", "start", "مورفو", "اهلا", "أهلا", "مرحبا"]
    if profile.state == UserProfileState.COMPLETE and profile_exists and message.lower() in greeting_triggers:
        reply = "أهلاً برجعتك! أنا MORVO 🤝 جاهز أساعدك. وش حاب نبدأ فيه اليوم؟"
        save_message_to_db(user_id, "user", message)
        save_message_to_db(user_id, "assistant", reply)
        if conversation_id:
            log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "welcome_back", "assistant", reply)
        return reply

    # Get conversation history and process message
    history = get_conversation_history(user_id)
    
    try:
        java_response = route_query(message)
        if java_response:
            response = java_response
        else:
            # Fallback to OpenAI with conversation history and profile context
            db_prof = _fetch_profile_from_db(str(user_uuid))
            prof_txt = ""
            if db_prof:
                parts = []
                if db_prof.get("user_role"): parts.append(f"role: {db_prof['user_role']}")
                if db_prof.get("industry"): parts.append(f"industry: {db_prof['industry']}")
                if db_prof.get("company_size"): parts.append(f"company_size: {db_prof['company_size']}")
                if db_prof.get("website_status"): parts.append(f"website: {db_prof['website_status']}")
                if db_prof.get("website_url"): parts.append(f"url: {db_prof['website_url']}")
                goals = db_prof.get("primary_goals")
                if isinstance(goals, list) and goals:
                    parts.append("goals: " + ", ".join([str(g) for g in goals][:5]))
                if db_prof.get("budget_range"): parts.append(f"budget: {db_prof['budget_range']}")
                prof_txt = "\nUser profile → " + "; ".join(parts)
            system_prompt = MORVO_SYSTEM_PROMPT + prof_txt
            response = answer_with_openai(message, system_text=system_prompt, history=history)

    except Exception as e:
        logging.error(f"Error in chat: {e}")
        response = f"عذراً، حدث خطأ في المعالجة. يرجى المحاولة مرة أخرى. (Error: {str(e)})"

    # Save messages to database
    save_message_to_db(user_id, "user", message)
    save_message_to_db(user_id, "assistant", response)

    # Log turns
    if conversation_id:
        log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "chat", "user", message)
        log_turn_via_rpc(user_uuid, conversation_id, profile, {}, "chat", "assistant", response)

    return response

def main():
    # Sidebar for user management
    with st.sidebar:
        st.title("⚙️ الإعدادات")
        
        if st.button("🔄 بدء جلسة جديدة"):
            st.session_state.user_id = generate_user_id()
            st.session_state.chat_history = []
            st.session_state.onboarding_state = None
            st.session_state.profile_complete = False
            st.rerun()
        
        if st.button("🗑️ مسح المحادثة"):
            if st.session_state.user_id:
                clear_conversation_history(st.session_state.user_id)
                st.session_state.chat_history = []
            st.rerun()
        
        st.divider()
        
        # Display user info
        if st.session_state.user_id:
            st.write(f"**معرف المستخدم:**")
            st.code(st.session_state.user_id[:8] + "...")
        
        # System status
        st.divider()
        st.write("**حالة النظام:**")
        if _sb:
            st.success("✅ Supabase متصل")
        else:
            st.error("❌ Supabase غير متصل")
        
        if os.getenv("OPENAI_API_KEY"):
            st.success("✅ OpenAI متصل")
        else:
            st.error("❌ OpenAI غير متصل")

    # Main content area
    if not st.session_state.user_id:
        # Welcome screen
        st.markdown("""
        <div class="welcome-card">
            <h1>مورفو 🤖</h1>
            <h2>مساعدك الذكي في التسويق</h2>
            <p>أنا مستشارك الذكي للتسويق، جاهز لمساعدتك في تحليل البيانات وتطوير استراتيجيات التسويق.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <h3>📊 تحليل السمعة</h3>
                <p>تحليل ذكر العلامة التجارية وسمعتها</p>
            </div>
            <div class="feature-card">
                <h3>📱 متابعة المنشورات</h3>
                <p>متابعة أداء المنشورات على وسائل التواصل</p>
            </div>
            <div class="feature-card">
                <h3>🔍 تحليل SEO</h3>
                <p>تحليل أداء SEO والكلمات المفتاحية</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 ابدأ الآن", type="primary", use_container_width=True):
            st.session_state.user_id = generate_user_id()
            st.rerun()
    
    else:
        # Chat interface
        st.title("💬 محادثة مع مورفو")
        
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>أنت:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>مورفو:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_input(
                    "اكتب رسالتك هنا...",
                    key="chat_input",
                    placeholder="اسألني أي سؤال تسويقي..."
                )
            
            with col2:
                if st.button("إرسال", type="primary", use_container_width=True):
                    if user_input.strip():
                        # Add user message to history
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": user_input
                        })
                        
                        # Get response from MORVO
                        with st.spinner("جاري المعالجة..."):
                            response = chat_with_mona(user_input, st.session_state.user_id)
                        
                        # Add assistant response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response
                        })
                        
                        # Clear input and rerun
                        st.session_state.chat_input = ""
                        st.rerun()

if __name__ == "__main__":
    main() 