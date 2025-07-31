from tools.perplexity_tool import fetch_perplexity_insight
from tools.almarai_tool import almarai_tool
from memory_store import get_user_memory
from schema import UserProfile
from langchain.agents import initialize_agent, AgentType
from tools.supabase_client import supabase
import re

def is_arabic(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))

def respond_with_future_vision(message: str) -> str | None:
    """
    Dynamically fetches roadmap replies from Supabase based on keywords.
    """
    try:
        response = supabase.table("features_roadmap").select("*").execute()
        rows = response.data or []
        lowered_message = message.lower()
        lang = "ar" if is_arabic(message) else "en"

        for row in rows:
            keyword = row.get("keyword", "").lower()
            if keyword in lowered_message:
                roadmap_msg = row.get(f"response_{lang}")
                if not roadmap_msg:
                    continue
                return (
                    f"{roadmap_msg}\n\n"
                    + (
                        "💡 مورفو دائماً في تطوّر — لأنه مبني على تقنيات ذكية وقادر على التكيف مع احتياجاتك بسرعة.\n"
                        "🚀 هذه الميزة ستكون جاهزة قريبًا، وبأسلوبه الذكي والمبسط، راح تكون تجربة التسويق عندك مختلفة تماماً!"
                        if lang == "ar"
                        else
                        "💡 MORVO is constantly evolving — built with intelligent tech and designed to adapt to your marketing needs fast.\n"
                        "🚀 This feature is coming soon, and with MORVO's conversational flow, your marketing experience will feel truly next-gen!"
                    )
                )
    except Exception as e:
        print("❌ Error fetching roadmap reply from Supabase:", e)
    
    return None

def create_mona_agent(user_id: str):
    tools = [
        fetch_perplexity_insight,
        almarai_tool  # Custom Supabase-based tool
    ]
    memory = get_user_memory(user_id)

    return initialize_agent(
        tools=tools,
        llm=None,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    # Check for roadmap reply
    future_reply = respond_with_future_vision(message)
    if future_reply:
        return future_reply

    # Fallback to Almarai tools or Perplexity
    agent = create_mona_agent(user_id)
    return agent.run(message)
