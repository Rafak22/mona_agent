from tools.perplexity_tool import fetch_perplexity_insight
from tools.almarai_mentions_tool import fetch_mentions_summary
from tools.almarai_seo_tool import fetch_seo_signals_summary
from tools.almarai_posts_tool import fetch_posts_summary
from memory_store import get_user_memory
from schema import UserProfile
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
import re

def is_arabic(text: str) -> bool:
    """Quick check: does the string contain Arabic letters?"""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def route_almarai_query(message: str) -> str | None:
    """
    Routes Almarai-related queries to the appropriate tool based on keywords.
    """
    message = message.lower().strip()

    # Keywords for different data types
    mentions_keywords = [
        "براند", "السمعة", "ذكر", "brand mentions", "reputation", "brand24"
    ]
    posts_keywords = [
        "منشور", "المنشورات", "السوشيال", "وسائل التواصل", "نشر", "محتوى", 
        "ayrshare", "post", "social media"
    ]
    seo_keywords = [
        "تحسين محركات", "seo", "تحليل الكلمات", "ترتيب", "تصدر", "البحث", 
        "موقع", "se ranking", "keyword ranking"
    ]

    if any(kw in message for kw in mentions_keywords):
        return fetch_mentions_summary()
    elif any(kw in message for kw in posts_keywords):
        return fetch_posts_summary()
    elif any(kw in message for kw in seo_keywords):
        return fetch_seo_signals_summary()
    
    return None

def create_mona_agent(user_id: str):
    """
    Creates a LangChain agent using the modern AgentExecutor pattern.
    """
    # Define tools with descriptions
    tools = [
        Tool(
            name="perplexity_insight",
            func=fetch_perplexity_insight.invoke,
            description="Use this tool for general marketing insights and analysis."
        )
    ]

    # Initialize LLM with low temperature for more focused responses
    llm = ChatOpenAI(temperature=0)

    # Create the agent with React framework
    agent = create_react_agent(llm=llm, tools=tools)

    # Wrap in executor with memory
    memory = get_user_memory(user_id)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )

    return agent_executor

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    """
    Main entry point for handling user queries.
    First tries to route Almarai-specific queries, then falls back to Perplexity.
    """
    # Try Almarai-specific routing first
    almarai_reply = route_almarai_query(message)
    if almarai_reply:
        return almarai_reply

    # Fallback to general Perplexity queries
    agent = create_mona_agent(user_id)
    try:
        return agent.invoke({"input": message})["output"]
    except Exception as e:
        print(f"Error in agent execution: {e}")
        return "عذراً، حدث خطأ في معالجة طلبك. هل يمكنك إعادة صياغة السؤال بطريقة مختلفة؟"