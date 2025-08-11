from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from tools.onboarding_persistence import persist_step_result
from tools.conversation_logger import to_uuid, get_or_create_conversation
from tools.supabase_client import supabase

# Steps constants
ROLE = "role_selection"
INDUSTRY = "industry_selection"
SIZE = "company_size"
WEBSITE_STATUS = "website_status"
WEBSITE_URL = "website_url_input"
GOALS = "goals_multi"
BUDGET = "budget_select"
DONE = "done"

# Option maps
ROLE_OPTIONS = [
    {"id": "marketing_manager", "label": "🏢 مدير/ة تسويق"},
    {"id": "marketing_specialist", "label": "📊 مختص/ة تسويق"},
    {"id": "entrepreneur", "label": "🚀 رائد/ة أعمال"},
    {"id": "general_manager", "label": "👔 مدير/ة عام"},
    {"id": "business_owner", "label": "💼 مالك/ة شركة"},
    {"id": "other", "label": "🎯 أخرى"},
]

INDUSTRY_OPTIONS = [
    {"id": "ecommerce", "label": "🛒 تجارة إلكترونية"},
    {"id": "healthcare", "label": "🏥 خدمات صحية"},
    {"id": "tech", "label": "💻 تقنية"},
    {"id": "construction", "label": "🏗 مقاولات"},
    {"id": "education", "label": "🎓 تعليم"},
    {"id": "restaurants", "label": "🍕 مطاعم"},
    {"id": "finance", "label": "💰 مالية"},
    {"id": "creative", "label": "🎨 إبداع"},
    {"id": "logistics", "label": "🚚 لوجستيات"},
    {"id": "other", "label": "✨ أخرى"},
]

SIZE_OPTIONS = [
    {"id": "solo", "label": "👤 فردي"},
    {"id": "small", "label": "👥 2–10"},
    {"id": "medium", "label": "🏢 11–50"},
    {"id": "large", "label": "🏗 51+"},
]

WEBSITE_STATUS_OPTIONS = [
    {"id": "active", "label": "✅ شغال"},
    {"id": "needs_work", "label": "🔧 يحتاج تطوير"},
    {"id": "under_construction", "label": "🏗 تحت الإنشاء"},
    {"id": "none", "label": "❌ ما عندنا"},
]

GOALS_OPTIONS = [
    {"id": "sales", "label": "📈 زيادة المبيعات"},
    {"id": "leads", "label": "👥 جذب عملاء"},
    {"id": "brand", "label": "🧭 بناء الهوية"},
    {"id": "analytics", "label": "📊 تحسين التحليلات"},
    {"id": "social", "label": "💬 السوشال ميديا"},
]

BUDGET_OPTIONS = [
    {"id": "lt5k", "label": "💸 <5K"},
    {"id": "k5_15", "label": "💰 5–15K"},
    {"id": "k15_50", "label": "💎 15–50K"},
    {"id": "gt50", "label": "🚀 >50K"},
    {"id": "later", "label": "🤔 لاحقًا"},
]


def _load_state(conversation_id: str) -> Dict[str, Any]:
    try:
        res = supabase.table("conversations").select("state").eq("id", conversation_id).limit(1).execute()
        if res.data:
            return res.data[0].get("state", {}) or {}
    except Exception:
        pass
    return {}


def start_step(user_id: str) -> Dict[str, Any]:
    user_uuid = to_uuid(user_id)
    conversation_id = get_or_create_conversation(user_uuid)
    agent_response = {
        "ui_type": "options",
        "message": "حياك الله! وش دورك في العمل؟",
        "options": ROLE_OPTIONS,
        "state_updates": {"current_step": ROLE}
    }
    # Persist empty state with current step
    state = _load_state(conversation_id)
    persist_step_result(user_uuid, conversation_id, state, agent_response, ROLE)
    return agent_response | {"conversation_id": conversation_id}


def next_step(user_id: str, conversation_id: str, current_step: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    user_uuid = to_uuid(user_id)
    state = _load_state(conversation_id)

    if current_step == ROLE:
        state["user_role"] = payload.get("value")
        agent_response = {"ui_type": "options", "message": "إيش نشاط شركتكم؟", "options": INDUSTRY_OPTIONS, "state_updates": {"industry": None}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, INDUSTRY)
        return agent_response

    if current_step == INDUSTRY:
        state["industry"] = payload.get("value")
        agent_response = {"ui_type": "options", "message": "طيب، كم حجم الشركة تقريبا؟", "options": SIZE_OPTIONS, "state_updates": {"company_size": None}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, SIZE)
        return agent_response

    if current_step == SIZE:
        state["company_size"] = payload.get("value")
        agent_response = {"ui_type": "options", "message": "عندكم موقع إلكتروني؟", "options": WEBSITE_STATUS_OPTIONS, "state_updates": {"website_status": None}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, WEBSITE_STATUS)
        return agent_response

    if current_step == WEBSITE_STATUS:
        status = payload.get("value")
        state["website_status"] = status
        if status in {"active", "needs_work", "under_construction"}:
            agent_response = {"ui_type": "input", "message": "أرسل رابط الموقع لو تكرمت:", "fields": [{"id": "website_url", "label": "رابط الموقع"}], "state_updates": {"website_url": None}}
            persist_step_result(user_uuid, conversation_id, state, agent_response, WEBSITE_URL)
            return agent_response
        # else jump to goals step
        agent_response = {"ui_type": "multi_select", "message": "وش أهم هدف لك الآن؟ (اختر واحد أو أكثر)", "options": GOALS_OPTIONS, "state_updates": {"primary_goals": []}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, GOALS)
        return agent_response

    if current_step == WEBSITE_URL:
        state["website_url"] = payload.get("value")
        agent_response = {"ui_type": "multi_select", "message": "وش أهم هدف لك الآن؟ (اختر واحد أو أكثر)", "options": GOALS_OPTIONS, "state_updates": {"primary_goals": []}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, GOALS)
        return agent_response

    if current_step == GOALS:
        # Expect list
        state["primary_goals"] = payload.get("values", [])
        agent_response = {"ui_type": "options", "message": "كم الميزانية التقريبية؟", "options": BUDGET_OPTIONS, "state_updates": {"budget_range": None}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, BUDGET)
        return agent_response

    if current_step == BUDGET:
        state["budget_range"] = payload.get("value")
        agent_response = {"ui_type": "input", "message": "تم! المعلومات اتحفظت. اكتب 'ابدأ' علشان نكمل.", "fields": [], "state_updates": {}}
        persist_step_result(user_uuid, conversation_id, state, agent_response, DONE)
        return agent_response

    # default fallback
    return start_step(user_id)