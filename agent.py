from langchain.agents import initialize_agent, AgentType
from tools.perplexity_tool import fetch_perplexity_insight
from tools.clinic_tool import fetch_clinic_info  # ✅ New import
from memory_store import get_user_memory
from schema import UserProfile

# Define keywords related to future tools
FUTURE_FEATURES = {
    "brand": "🛠️ I’ll soon be able to monitor your brand using Brand24 and notify you of every mention.",
    "brand24": "🛠️ Brand24 integration is on the roadmap. Soon I’ll track your mentions across the web.",
    "keyword": "📈 Keyword tracking via SE Ranking is coming soon. I’ll give you full SEO insights in future phases.",
    "seo": "📈 SE Ranking will power SEO insights in the near future — I’m getting smarter each day!",
    "ranking": "📈 SE Ranking-based features are coming up. Stay tuned!",
    "social": "📣 I’ll soon manage your social media through Ayrshare — from posting to scheduling campaigns!",
    "ayrshare": "📣 Social media management via Ayrshare is part of the next version of my abilities.",
    "post on social": "📣 That’s coming! I’ll soon be posting on your behalf using Ayrshare.",
}

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

def respond_with_future_vision(message: str) -> str | None:
    lowered = message.lower()
    for keyword, future_response in FUTURE_FEATURES.items():
        if keyword in lowered:
            return f"{future_response}\n\n🧠 I’m constantly evolving — this feature will be available in a future update!"
    return None

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    # Check if it's a question about future tool features
    future_reply = respond_with_future_vision(message)
    if future_reply:
        return future_reply

    # Run Mona agent with LangChain tools (Perplexity + Clinic)
    agent = create_mona_agent(user_id)
    return agent.run(message)
