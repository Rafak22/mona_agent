from langchain.agents import initialize_agent, AgentType
from tools.perplexity_tool import fetch_perplexity_insight
from memory_store import get_user_memory

def create_mona_agent(user_id: str):
    tools = [fetch_perplexity_insight]  # Mona's only tool is Perplexity
    memory = get_user_memory(user_id)

    return initialize_agent(
        tools=tools,
        llm=None,  # No OpenAI LLM
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
    )

def run_agent(user_id: str, message: str):
    agent = create_mona_agent(user_id)
    return agent.run(message)
 