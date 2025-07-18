from langchain.memory import ConversationBufferMemory
from schema import UserProfile

user_memory = {}
users = {}

def get_user_memory(user_id: str):
    if user_id not in user_memory:
        user_memory[user_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return user_memory[user_id]

def get_user_profile(user_id: str) -> UserProfile:
    if user_id not in users:
        users[user_id] = UserProfile()
    return users[user_id]

def update_user_profile(user_id: str, profile: UserProfile):
    users[user_id] = profile 