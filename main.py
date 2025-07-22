
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schema import UserMessage, UserProfileState
from memory_store import get_user_profile, update_user_profile, get_user_memory
from tools.perplexity_tool import fetch_perplexity_insight
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS settings
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

@app.post("/chat")
def chat_with_mona(user_input: UserMessage):
    profile = get_user_profile(user_input.user_id)
    memory = get_user_memory(user_input.user_id)
    message = user_input.message.strip()

    # Onboarding Step 1: Ask Name
    if profile.state == UserProfileState.ASK_NAME:
        if message.startswith("أنا اسمي") or message.startswith("اسمي"):
            name = message.replace("أنا اسمي", "").replace("اسمي", "").strip()
        else:
            name = message.strip()

        profile.name = name
        profile.state = UserProfileState.ASK_TITLE
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": f"✨ تشرفت فيك يا {profile.name}!\nWhat's your title?"
        }

    # Onboarding Step 2: Ask Title
    elif profile.state == UserProfileState.ASK_TITLE:
        profile.title = message
        profile.state = UserProfileState.ASK_ROLE
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": "📌 ممتاز!\nNow tell me your role inside the company."
        }

    # Onboarding Step 3: Ask Role
    elif profile.state == UserProfileState.ASK_ROLE:
        profile.role = message
        profile.state = UserProfileState.ASK_GOAL
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": "🎯 عظيم!\nWhat's your business goal?"
        }

    # Onboarding Step 4: Ask Goal
    elif profile.state == UserProfileState.ASK_GOAL:
        profile.goal = message
        profile.state = UserProfileState.COMPLETE
        update_user_profile(user_input.user_id, profile)
        return {
            "reply": f"🔥 جاهزين يا {profile.name}!\nNow you can ask me anything about marketing 🚀"
        }

    # ✅ Post-onboarding: Use Perplexity + Memory
    elif profile.state == UserProfileState.COMPLETE:
        chat_history = memory.load_memory_variables({})["chat_history"]

        full_context = f"{profile.name}, a {profile.title}, working as a {profile.role}, wants to achieve: {profile.goal}."

        final_prompt = f"""User profile:
{full_context}

Previous chat history:
{chat_history}

User question:
{message}

Please structure your answer clearly using sections and bullet points only (avoid tables). Format the response in a way that can be easily transformed into visual blocks or graphs in the UI. Use clear headings and short paragraphs, and organize information logically by phases or stages.
"""

        memory.chat_memory.add_user_message(message)
        response = fetch_perplexity_insight(final_prompt)
        memory.chat_memory.add_ai_message(response)

        return {"reply": response}

