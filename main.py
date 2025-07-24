import json
import logging
import textwrap
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import UserMessage, UserProfileState, UserProfile
from memory_store import get_user_profile, update_user_profile, users, user_memory
from tools.perplexity_tool import fetch_perplexity_insight
from tools.clinic_tool import fetch_clinic_info
from agent import respond_with_future_vision
from dotenv import load_dotenv

# Load .env and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

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
        "العيادة", "باسم", "الموقع", "الخدمات", "الفئة المستهدفة", "عيادة",
        "سوق العيادات", "الخدمات الطبية", "أوقات العمل", "ساعات العمل", "الرؤية", "الرؤية المستقبلية",
        "روابط", "انستغرام", "تيك توك", "التواصل الاجتماعي", "وصف", "من أنتم", "ما هي",
        "clinic", "bassim", "location", "services", "target audience",
        "goals", "marketing goals", "market size", "clinic market", 
        "current marketing", "challenges", "clinic size", "vision", "business hours",
        "working hours", "social media", "description", "what does the clinic offer"
    ]
    return any(kw in message for kw in keywords)

def is_future_tool_question(msg: str) -> bool:
    future_keywords = ["brand24", "se ranking", "ayrshare", "future tool", "أداة", "ميزة", "قريبًا"]
    return any(tool in msg for tool in future_keywords)

@app.post("/chat")
def chat_with_mona(user_input: UserMessage):
    if not user_input.user_id:
        return {
            "reply": "مرحباً أستاذ سعد، أنا مورفو، وكيلتك التسويقية الذكية. جاهزة أساعدك تحقق أهدافك التسويقية — من وين تحب نبدأ اليوم؟"
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
                "مستر سعد، أنا **MORVO** — مو مجرد أداة ذكاء اصطناعي، بل رؤية جديدة كليًا تعيد تعريف التسويق كما نعرفه.\n\n"
                "Mr. Saad, I'm **MORVO**, and I represent something that hasn't existed before — "
                "an AI marketing agent that doesn’t just assist with marketing, but **completely reimagines it**.\n\n"
                "بينما يُنفق السوق أكثر من **350 مليار دولار سنويًا** على استراتيجيات مبنية على الحدس والتجريب، "
                "أنا أعمل بدقة رياضية **(mathematical precision)**، وأحلل أنماط السوق بطريقة تفوق قدرات البشر.\n\n"
                "What you're looking at is **not another AI tool** — it's the **transformation of marketing** from an art into a measurable science. "
                "I've already identified opportunities your competitors missed, and with your vision and investment, "
                "أقدر أوسع هذا الذكاء ليُحدث ثورة في طريقة تواصلكم مع جمهوركم.\n\n"
                "💡 *المستقبل ما راح يجي — هو هنا الآن. وأنا جاهز أتعاون مع أصحاب الرؤية اللي يقدّرون قيمة التحول الحقيقي.*\n\n"
                "🔑 **القدرات الأساسية | Key Capabilities**:\n"
                "📈 أشوف الفرص اللي منافسيك ما شافوها.\n"
                "📊 قريبًا بتكامل مع أدوات مثل SE Ranking، Brand24، وغيرها.\n"
                "🔁 أمتلك القابلية للتوسع الفوري — من شركة ناشئة إلى علامة تجارية عملاقة."
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

    if is_clinic_related(message):
        clinic_reply = fetch_clinic_info.run(message)
        if "❓" not in clinic_reply and "more clarity" not in clinic_reply.lower():
            return {"reply": clinic_reply}

    if is_future_tool_question(message):
        future_reply = respond_with_future_vision(message)
        if future_reply and ("قريبًا" in future_reply or "coming soon" in future_reply):
            return {"reply": future_reply}

    full_context = f"{profile.name}, a {profile.title}, working as a {profile.role}, wants to achieve: {profile.goal}."
    prompt_base = f"Context:\n{full_context}\n\nUser question:\n{message}"
    shortened_prompt = textwrap.shorten(prompt_base, width=1000, placeholder="...")

    final_prompt = (
        f"{shortened_prompt}\n\n"
        "Respond with short and powerful insights using Perplexity. "
        "Keep total response between 40–100 words. Make it concise, well-structured, bullet-pointed where helpful, "
        "and clear enough to fit inside UI blocks."
    )

    praise = (
        "🤖 أنا مورفو، وكيلة تسويق ذكية مبنية على تقنيات متقدمة. أقدر أوفر لك إجابات فعالة ومباشرة.\n\n"
        if "arabic" in profile.goal.lower() or any("\u0600" <= c <= "\u06FF" for c in message)
        else "🤖 I'm MORVO — ROI-focused and sharp. Let’s get straight to what matters.\n\n"
    )

    response = fetch_perplexity_insight.invoke(praise + final_prompt)
    return {"reply": response}

class CompanyRequest(BaseModel):
    company_name: str
    user_id: str

@app.post("/360prep")
def generate_360_report(req: CompanyRequest):
    intro = "📊 360° Snapshot by MORVO & Perplexity:\n\n"
    prompt = f"""Give a short marketing snapshot for {req.company_name}.

Include:
- Branding
- Content
- Social Media
- Website SEO
- Competitor edge

Keep it short, 40–100 words, bullet format, good for fast scan.
"""
    response = fetch_perplexity_insight.invoke(intro + prompt)
    return {"reply": response}
