import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import UserMessage, UserProfileState
from memory_store import get_user_profile, update_user_profile
from tools.perplexity_tool import fetch_perplexity_insight
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# 👇 Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify domains like ["https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "👋 Mona is ready to help you 3x your ROI!"}

@app.post("/chat")
def chat_with_mona(user_input: UserMessage):
    profile = get_user_profile(user_input.user_id)
    message = user_input.message.strip()

    # 🧠 Step-by-step onboarding
    if profile.state == UserProfileState.ASK_NAME:
        profile.name = message
        profile.state = UserProfileState.ASK_TITLE
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": f"✨ تشرفت فيك يا {profile.name}! What's your title or مسماك الوظيفي؟"
        }

    elif profile.state == UserProfileState.ASK_TITLE:
        profile.title = message
        profile.state = UserProfileState.ASK_ROLE
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": "📌 ممتاز! Now tell me your role – دورك الوظيفي داخل العمل؟"
        }

    elif profile.state == UserProfileState.ASK_ROLE:
        profile.role = message
        profile.state = UserProfileState.ASK_GOAL
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": "🎯 Great! What's your business goal? (وش تبغى تحقق تجاريًا؟)"
        }

    elif profile.state == UserProfileState.ASK_GOAL:
        profile.goal = message
        profile.state = UserProfileState.COMPLETE
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": f"🔥 جاهزين يا {profile.name}! Now you can ask me anything about marketing 🚀"
        }

    # 🧠 After onboarding — use Perplexity
    elif profile.state == UserProfileState.COMPLETE:
        full_context = f"{profile.name}, a {profile.title}, working as a {profile.role}, wants to achieve: {profile.goal}."
        final_prompt = f"User profile:\n{full_context}\n\nUser question: {message}"
        response = fetch_perplexity_insight(final_prompt)
        return {"reply": response} 