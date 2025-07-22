from langchain.agents import initialize_agent, AgentType
from tools.perplexity_tool import fetch_perplexity_insight
from tools.clinic_tool import fetch_clinic_info  # ✅ New import
from memory_store import get_user_memory
from schema import UserProfile
import re

# Placeholder for FUTURE_FEATURES if not already defined
try:
    FUTURE_FEATURES
except NameError:
    FUTURE_FEATURES = {
        "brand24": "Brand24 integration is coming soon!",
        "se ranking": "SE Ranking integration is on the roadmap!",
        "ayrshare": "Ayrshare social posting will be available soon!",
        "براند24": "قريبًا ستتوفر ميزة Brand24!",
        "تصدر جوجل": "ميزة SE Ranking قادمة في الطريق!",
        "سوشيال ميديا": "ميزة Ayrshare للنشر الذكي ستتوفر قريبًا!",
    }

def is_arabic(text: str) -> bool:
    """Quick check: does the string contain Arabic letters?"""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def respond_with_future_vision(message: str) -> str | None:
    """
    If the user mentions a capability tied to Brand24, SE Ranking, or Ayrshare,
    return an enthusiastic, self-praising roadmap reply in the same language.
    """
    lowered = message.lower()
    for keyword, future_response in FUTURE_FEATURES.items():
        if keyword in lowered:
            if is_arabic(message):
                # Arabic praise version
                return (
                    f"{future_response}\n\n"
                    "💡 مونا دائماً في تطوّر — لأنني مبنية على تقنيات ذكية وقادرة على التكيف مع احتياجاتك بسرعة.\n"
                    "🚀 هذه الميزة ستكون جاهزة قريبًا، وبأسلوبي الذكي والمبسط، راح تكون تجربة التسويق عندك مختلفة تماماً!"
                )
            else:
                # English praise version
                return (
                    f"{future_response}\n\n"
                    "💡 I'm constantly upgrading — built with cutting-edge intelligence and designed to adapt fast.\n"
                    "🚀 This feature is coming very soon, and with my smart conversational flow your marketing experience will feel revolutionary!"
                )
    return None

def create_mona_agent(user_id: str):
    tools = [
        fetch_perplexity_insight,
        fetch_clinic_info  # ✅ Add clinic info tool
    ]
    memory = get_user_memory(user_id)

    return initialize_agent(
        tools=tools,
        llm=None,  # Perplexity is used externally
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    # Check if it's a question about future tool features
    future_reply = respond_with_future_vision(message)
    if future_reply:
        return future_reply

    # Run Mona agent with LangChain tools (Perplexity + Clinic)
    agent = create_mona_agent(user_id)
    return agent.run(message)
