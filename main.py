import logging
import textwrap
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.perplexity_tool import fetch_perplexity_insight
from agent import run_agent
from dotenv import load_dotenv

# Load .env and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "👋 MORVO is ready to analyze Almarai data!"}

@app.post("/chat")
def chat_with_mona(user_input: UserMessage):
    if not user_input.user_id:
        return {
            "reply": "مرحباً! أنا مورفو، وكيلتك التسويقية الذكية. جاهزة لتحليل بيانات المراعي — من وين تحب نبدأ اليوم؟"
        }

    profile = get_user_profile(user_input.user_id)
    message = user_input.message.strip()

    if message == "start over":
        profile.state = UserProfileState.CONFIRM_RESET
        update_user_profile(user_input.user_id, profile)
        return {"reply": "⚠️ هل أنت متأكد أنك تريد البدء من جديد؟ اكتب: نعم"}

    if profile.state == UserProfileState.CONFIRM_RESET:
        if message == "نعم":
            users[user_input.user_id] = UserProfile()
            if user_input.user_id in user_memory:
                del user_memory[user_input.user_id]
            return {"reply": "🔄 تم إعادة تعيين المحادثة. أهلاً من جديد! ما اسمك؟"}
        else:
            profile.state = UserProfileState.COMPLETE
            update_user_profile(user_input.user_id, profile)
            return {"reply": "❌ تم إلغاء إعادة التهيئة. نكمل من وين وقفنا 😊"}

    if profile.state == UserProfileState.COMPLETE and message.lower() in ["", "hi", "hello", "ابدأ", "start", "مورفو"]:
        return {
            "reply": (
                "أهلاً! أنا **MORVO** — وكيلتك التسويقية الذكية المتخصصة في تحليل بيانات المراعي.\n\n"
                "🔍 أقدر أساعدك في:\n"
                "• تحليل ذكر العلامة التجارية وسمعتها\n"
                "• متابعة أداء المنشورات على وسائل التواصل\n"
                "• تحليل أداء SEO والكلمات المفتاحية\n\n"
                "💡 من وين تحب نبدأ اليوم؟"
            )
        }

    # Route message through agent
    response = run_agent(user_input.user_id, message, profile)
    return {"reply": response}

# For the 360° feature
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
    response = fetch_perplexity_insight.invoke(intro + prompt)
    return {"reply": response}