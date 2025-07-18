from langchain.agents import initialize_agent, AgentType
from tools.perplexity_tool import fetch_perplexity_insight
from memory_store import get_user_memory

def create_mona_agent(user_id: str):
    tools = [fetch_perplexity_insight]  # Mona's only tool is Perplexity
    memory = get_user_memory(user_id)

    return initialize_agent(
        tools=tools,
        llm=None,  # ❌ No OpenAI LLM
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Simplest reactive agent
        verbose=True,
        memory=memory,
    )

def run_agent(message: str):
    return agent.run(message)

def get_next_question(state: UserProfileState) -> tuple[str, UserProfileState]:
    steps = ["title", "role", "company", "website", "team_size"]
    for step in steps:
        if state.get(step) is None:
            state["current_step"] = step
            return ask_question_for(step), state
    # All steps done
    return "Thank you! I have all the info I need.", state

def ask_question_for(step: str) -> str:
    questions = {
        "title": "What's your job title?",
        "role": "What’s your role in the company?",
        "company": "What's the name of your company?",
        "website": "Do you have a company website?",
        "team_size": "How many people are on your team?",
    }
    return questions.get(step, "Can you tell me more?") 