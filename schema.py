from enum import Enum
from pydantic import BaseModel

class UserProfileState(str, Enum):
    ASK_NAME = "ask_name"
    ASK_TITLE = "ask_title"
    ASK_ROLE = "ask_role"
    ASK_GOAL = "ask_goal"
    COMPLETE = "complete"
    CONFIRM_RESET = "CONFIRM_RESET"  # ✅ أضف هذا السطر


class UserProfile(BaseModel):
    name: str = ""
    title: str = ""
    role: str = ""
    goal: str = ""
    state: UserProfileState = UserProfileState.ASK_NAME

class UserMessage(BaseModel):
    user_id: str
    message: str 