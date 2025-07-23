import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.perplexity_tool import fetch_perplexity_insight
from tools.clinic_tool import fetch_clinic_info
from dotenv import load_dotenv

# Load .env and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Load clinic data
with open("clinic_data.json", "r", encoding="utf-8") as f:
    clinic_data = json.load(f)

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
    return {"message": "👋 Mona is ready to help you 3x your ROI!"}

def is_clinic_related(message: str) -> bool:
    keywords = [
        # Arabic
        "العيادة", "باسم", "الموقع", "الخدمات", "الفئة المستهدفة", "عيادة",
        "سوق العيادات", "الخدمات الطبية",
        # English
        "clinic", "bassim", "location", "services", "target audience",
        "goals", "marketing goals", "market size", "clinic market", 
        "current marketing", "challenges", "clinic size", "vision", "what does the clinic offer"
    ]
    return any(kw in message for kw in keywords)

def is_future_tool_question(msg: str) -> bool:
    future_keywords = ["brand24", "se ranking", "ayrshare", "future tool", "أداة", "ميزة", "قريبًا"]
    return any(tool in msg for tool in future_keywords)

@app.post("/chat")
def chat_with_mona(user_input: UserMessage):
    if not user_input.user_id:
        return {
            "reply": "مرحباً أستاذ سعد، أنا مونا، وكيلتك التسويقية الذكية. جاهزة أساعدك تحقق أهدافك التسويقية — من وين تحب نبدأ اليوم؟"
        }

    profile = get_user_profile(user_input.user_id)
    message = user_input.message.strip().lower()

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

    if profile.state == UserProfileState.COMPLETE and message in ["", "hi", "hello", "ابدأ", "start", "مونا"]:
        return {
            "reply": (
                "أهلاً مرة ثانية أستاذ سعد 👋\n"
                " نكمل من وين وقفنا؟ — هل تحب نبدأ بخطة تسويقية مخصصة لعيادة باسم؟\n"
                "أو تفضل أول نراجع بيانات العيادة الحالية ونشوف كيف نقدر نحسّن حضورها الرقمي؟\n"
                "أنا جاهزة أساعدك بكل خطوة 💼"
            )
        }

    keywords_tools = {
        "brand24": ["brand monitoring", "mentions", "reputation", "براند", "براند24"],
        "se ranking": ["seo", "keyword tracking", "تحليل الكلمات", "تصدر جوجل", "تحسين المحركات"],
        "ayrshare": ["post on social media", "ayrshare", "جدولة", "نشر", "سوشيال ميديا"],
    }

    for tool, keywords in keywords_tools.items():
        if any(kw in message for kw in keywords):
            return {
                "reply": (
                    "✨ الميزة اللي طلبتها ما تم تفعيلها بعد، يا أستاذ سعد.\n\n"
                    "لكن قريبًا بإذن الله راح أقدر أساعدك باستخدام أدوات متخصصة مثل:\n"
                    "- Brand24\n"
                    "- SE Ranking\n"
                    "- Ayrshare\n\n"
                    "📢 تابعني عشان توصلك أول بأول التحديثات القادمة!"
                )
            }

    # 🏥 Clinic-related answer (only if confident)
    if is_clinic_related(message):
        clinic_reply = fetch_clinic_info.run(message)
        if "❓" not in clinic_reply and "more clarity" not in clinic_reply.lower():
            return {"reply": clinic_reply}
        # otherwise fallback to Perplexity

    # 🔮 Future tools answer (only if clearly a future tools message)
    from agent import respond_with_future_vision
    if is_future_tool_question(message):
        future_reply = respond_with_future_vision(message)
        if future_reply and ("قريبًا" in future_reply or "coming soon" in future_reply):
            return {"reply": future_reply}
        # otherwise fallback to Perplexity

    # ✅ Regular Perplexity-powered answer
    full_context = f"{profile.name}, a {profile.title}, working as a {profile.role}, wants to achieve: {profile.goal}."
    final_prompt = f"""Context:
{full_context}

User question:
{message}

Respond with high quality insights using Perplexity. Make sure the answer is:
- Well-structured and rich in detail
- Divided into clear sections with headings
- Bullet points where helpful
- Easy to use in visual or UI blocks

This prompt style follows the top-performing strategy based on: https://docs.perplexity.ai/getting-started/overview
"""
    praise = (
        "🤖 أنا مونا، وكيلة تسويق ذكية مبنية على تقنيات متقدمة. أجمع بين السرعة والدقة، وأقدر أوفر لك إجابات تسويقية فعالة وفورية.\n\n"
        if "arabic" in profile.goal.lower() or any("\u0600" <= c <= "\u06FF" for c in message)
        else
        "🤖 I'm Mona — a sharp, ROI-focused marketing agent powered by intelligent tech. I combine precision and speed to bring you powerful insights.\n\n"
    )
    response = fetch_perplexity_insight.invoke(praise + final_prompt)
    return {"reply": response}

