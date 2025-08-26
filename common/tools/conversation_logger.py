import uuid
from typing import Optional, Dict, Any
from tools.supabase_client import supabase
from schema import UserProfile

# Generate a stable UUIDv5 from any string user_id so it fits UUID columns
# This ensures the same string always maps to the same UUID

def to_uuid(user_id_str: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id_str))


def get_or_create_conversation(user_uuid: str) -> Optional[str]:
    try:
        # Try to fetch the latest conversation for the user
        res = supabase.table("conversations").select("id").eq("user_id", user_uuid).order("created_at", desc=True).limit(1).execute()
        if res.data:
            return res.data[0]["id"]
        # Create a new conversation
        insert_res = supabase.table("conversations").insert({
            "user_id": user_uuid,
            "current_step": None,
            "state": {}
        }).execute()
        if insert_res.data:
            return insert_res.data[0]["id"]
    except Exception as e:
        print(f"⚠️ conversation init error: {e}")
    return None


def log_turn_via_rpc(
    user_uuid: str,
    conversation_id: str,
    profile: UserProfile,
    state_patch: Dict[str, Any],
    current_step: str,
    role: str,
    content_text: str,
    meta: Optional[Dict[str, Any]] = None
) -> None:
    try:
        payload = {
            "p_user_id": user_uuid,
            "p_conversation_id": conversation_id,
                                        "p_profile": {
                                "user_role": profile.role,
                                "industry": state_patch.get("industry"),
                                "company_size": state_patch.get("company_size"),
                                "website_status": state_patch.get("website_status"),
                                "website_url": state_patch.get("website_url"),
                                "primary_goals": state_patch.get("primary_goals", []) if isinstance(state_patch.get("primary_goals"), list) else [],
                                "budget_range": state_patch.get("budget_range"),
                            },
            "p_state_patch": state_patch or {},
            "p_current_step": current_step,
            "p_role": role,
            "p_content": {"text": content_text},
            "p_meta": meta or {},
        }
        supabase.rpc("log_turn", payload).execute()
    except Exception as e:
        print(f"⚠️ log_turn RPC error: {e}")
        # Continue execution even if logging fails