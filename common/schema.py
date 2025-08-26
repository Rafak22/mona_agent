from enum import Enum
from pydantic import BaseModel

class UserProfileState(str, Enum):
    NEW = "NEW"
    IN_ONBOARDING = "IN_ONBOARDING"
    COMPLETE = "COMPLETE"
    CONFIRM_RESET = "CONFIRM_RESET"

class UserProfile(BaseModel):
    name: str = ""
    title: str = ""
    role: str = ""
    goal: str = ""
    state: UserProfileState = UserProfileState.NEW

class UserMessage(BaseModel):
    user_id: str
    message: str
