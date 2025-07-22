import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.perplexity_tool import fetch_perplexity_insight
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
        "العيادة", "باسم", "الموقع", "الخدمات", "الفئة المستهدفة",
        "عيادة", "marketing in health", "health clinic", "سوق العيادات", "الخدمات الطبية"
    ]
    return any(kw in message for kw in keywords)

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
                "مرحباً أستاذ سعد، أنا مونا، وكيلتك التسويقية الذكية. "
                "جاهزة أساعدك تحقق أهدافك التسويقية — من وين تحب نبدأ اليوم؟\n\n"
                "- 📅 بناء خطة تسويقية أسبوعية\n"
                "- 📄 تحليل خطة PDF\n"
                "- 💡 اقتراح أفكار محتوى\n"
                "- 📊 عرض أداء الحملة"
            )
        }

    keywords_tools = {
        "brand24": ["brand monitoring", "mentions", "reputation", "براند", "براند24"],
        "se ranking": ["seo", "keyword tracking", "تحليل كلمات", "تصدر جوجل", "تحسين محركات"],
        "ayrshare": ["post on social media", "ayrshare", "جدولة", "نشر", "سوشيال ميديا"],
    }

    for tool, keywords in keywords_tools.items():
        if any(kw in message for kw in keywords):
            return {
                "reply": (
                    f"🔧 الميزة اللي طلبتها لسه ما فعّلتها يا أستاذ {profile.name}، "
                    "لكن قريبًا راح أقدر أساعدك باستخدام أدوات متخصصة مثل "
                    "Brand24, SE Ranking, و Ayrshare.\n"
                    "تابعني عشان تعرف أول بأول التحديثات القادمة 💡"
                )
            }

    if is_clinic_related(message):
        return {
            "reply": (
                f"🏥 معلومات عن عيادة باسم:\n"
                f"- 📍 الموقع: {clinic_data['location']}\n"
                f"- 🏢 الحجم: {clinic_data['size']}\n"
                f"- 💼 الخدمات: {', '.join(clinic_data['services'])}\n"
                f"- 🎯 الأهداف: {clinic_data['goals']}\n"
                f"- 👥 الفئة المستهدفة: {clinic_data['audience']}\n"
                f"- 📈 جهود التسويق الحالية: {clinic_data['current_marketing']}\n"
                f"- ❗ التحديات: {clinic_data['challenges']}\n\n"
                f"📊 حجم سوق العيادات الصحية في السعودية: {clinic_data['market_size']}"
            )
        }

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
    response = fetch_perplexity_insight(final_prompt)
    return {"reply": response}

