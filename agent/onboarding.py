import httpx
from typing import Optional, Dict, Any
import os

# Required fields for onboarding completion
REQUIRED_FIELDS = ["name", "role", "goal"]

async def fetch_profile(user_id: str, base_url: str) -> Dict[str, Any]:
    """Fetch user profile from Supabase proxy"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{base_url}/profiles/{user_id}")
            if response.status_code == 404:
                return {"user_id": user_id}
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"user_id": user_id}
            raise
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return {"user_id": user_id}

async def save_profile(user_id: str, base_url: str, partial_dict: Dict[str, Any]) -> bool:
    """Save partial profile to Supabase proxy"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.patch(f"{base_url}/profiles/{user_id}", json=partial_dict)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

def next_missing(profile: Dict[str, Any]) -> Optional[str]:
    """Get the first missing required field"""
    for field in REQUIRED_FIELDS:
        value = profile.get(field)
        if value is None or str(value).strip() == "":
            return field
    return None


def _is_valid_name(text: str) -> bool:
    return len(text.strip()) >= 2


def _is_valid_role(text: str) -> bool:
    return len(text.strip()) >= 2


def _is_valid_goal(text: str) -> bool:
    return len(text.strip()) >= 2


async def handle_onboarding(user_id: str, message: str, supabase_api: str) -> Optional[Dict[str, Any]]:
    """Handle onboarding flow - returns None if done, or dict with reply and step.
    This version does NOT rely on storing an _awaiting flag in Supabase to avoid schema changes.
    It infers the next field based on which required fields are missing and validates the user's latest message accordingly.
    """
    profile = await fetch_profile(user_id, supabase_api)

    # If complete, proceed to normal chat
    missing = next_missing(profile)
    if not missing:
        return None

    # Determine which field we should attempt to fill now
    # Always fill in order: name -> role -> goal
    if missing == "name":
        if _is_valid_name(message):
            await save_profile(user_id, supabase_api, {"name": message.strip()})
            return {
                "reply": "ممتاز! وش منصبك الحالي؟ (مثل: مدير تسويق، صاحب شركة، الخ)",
                "step": "role"
            }
        else:
            return {
                "reply": "حياك الله! وش اسمك الأول؟ (حرفين على الأقل)",
                "step": "name"
            }

    # Re-fetch to see if name got filled in another session
    profile = await fetch_profile(user_id, supabase_api)
    if next_missing(profile) == "role":
        if _is_valid_role(message) and profile.get("name"):
            await save_profile(user_id, supabase_api, {"role": message.strip()})
            return {
                "reply": "رائع! وش هدفك الأساسي من التسويق؟ (مثل: زيادة المبيعات، بناء العلامة التجارية، الخ)",
                "step": "goal"
            }
        else:
            return {
                "reply": "وش منصبك الحالي؟ (مثل: مدير تسويق، صاحب شركة، الخ)",
                "step": "role"
            }

    # Re-fetch again to ensure we have role
    profile = await fetch_profile(user_id, supabase_api)
    if next_missing(profile) == "goal":
        if _is_valid_goal(message) and profile.get("role"):
            await save_profile(user_id, supabase_api, {
                "goal": message.strip(),
                "state": "COMPLETE"
            })
            return {
                "reply": "تمّت عملية التعريف ✅ نبدأ؟ اسألني أي شي.",
                "step": "done"
            }
        else:
            return {
                "reply": "وش هدفك الأساسي من التسويق؟ (مثل: زيادة المبيعات، بناء العلامة التجارية، الخ)",
                "step": "goal"
            }

    # Default question (fallback)
    return {
        "reply": "خلّينا نبدأ بالتعارف… وش اسمك الأول؟",
        "step": "name"
    }
