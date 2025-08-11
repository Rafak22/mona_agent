import json
from .supabase_client import supabase

def persist_step_result(user_id: str, conversation_id: str, state: dict, agent_response: dict, current_step: str) -> None:
    # 1) profiles upsert
    supabase.table("profiles").upsert({
        "user_id": user_id,
        "user_role": state.get("user_role"),
        "industry": state.get("industry"),
        "company_size": state.get("company_size"),
        "website_status": state.get("website_status"),
        "website_url": state.get("website_url"),
        "primary_goals": state.get("primary_goals", []),
        "budget_range": state.get("budget_range"),
    }).execute()

    # 2) conversations update (merge state)
    supabase.table("conversations").update({
        "current_step": current_step,
        "state": state,
    }).eq("id", conversation_id).execute()

    # 3) conversation_turns insert (assistant response)
    supabase.table("conversation_turns").insert({
        "conversation_id": conversation_id,
        "user_id": user_id,
        "role": "assistant",
        "content": json.dumps(agent_response, ensure_ascii=False),
        "step": current_step,
    }).execute()