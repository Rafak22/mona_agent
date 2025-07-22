from enum import Enum
from pydantic import BaseModel

class UserProfileState(str, Enum):
    ASK_NAME = "ask_name"
    ASK_TITLE = "ask_title"
    ASK_ROLE = "ask_role"
    ASK_GOAL = "ask_goal"
    COMPLETE = "complete"
    CONFIRM_RESET = "CONFIRM_RESET"

class UserProfile(BaseModel):
    name: str = "سعد"
    title: str = "Founder"
    role: str = "Marketing Director"
    goal: str = "زيادة ROI عبر حملات فعّالة"
    state: UserProfileState = UserProfileState.COMPLETE

class UserMessage(BaseModel):
    user_id: str
    message: str
