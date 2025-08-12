# onboarding_graph.py
from typing import TypedDict, Literal, Optional, List, Dict, Any
from typing_extensions import NotRequired
import os, re

from langgraph.graph import StateGraph, START, END
import uuid
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

# ---------- Supabase (safe: if not configured, saving is skipped) ----------
try:
    from supabase import create_client, Client  # supabase-py v2
except Exception:
    create_client = None
    Client = None  # type: ignore

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
_sb: Optional["Client"] = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        _sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[supabase] init failed: {e}")
        _sb = None

# Only write the columns that EXIST in your table
_ALLOWED_DB_KEYS = {
    "user_id",
    "user_role",
    "industry",
    "company_size",
    "website_status",
    "website_url",
    "primary_goals",
    "budget_range",
}

# ---------- State schema ----------
class UIBlock(TypedDict, total=False):
    ui_type: Literal["options", "input"]
    message: str
    options: NotRequired[List[str]]

class OBState(TypedDict, total=False):
    user_id: str
    profile: Dict[str, Any]        # holds the DB fields listed above
    ui: UIBlock
    user_name: Optional[str]
    preferred_name: Optional[str]
    preferred_choice: Optional[str]

# ---------- Helpers ----------
def ask(message: str, *, options: Optional[List[str]] = None,
        ui_type: Literal["options","input"] = "input") -> Any:
    payload: UIBlock = {"ui_type": ui_type, "message": message}
    if options:
        payload["options"] = options
    return interrupt(payload)

_AR = re.compile(r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s\-']{1,40}$")
_LAT = re.compile(r"^[A-Za-z\s\-']{1,40}$")

def _clean_name(s: str) -> Optional[str]:
    s = (s or "").strip()
    if not s:
        return None
    if _AR.match(s) or _LAT.match(s):
        return s if not s.isascii() else s.title()
    return None

_URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
def _clean_url(s: str) -> Optional[str]:
    s = (s or "").strip()
    return s if s and _URL_RE.match(s) else None

def _to_uuid_str(user_id: str) -> str:
    """Return a valid UUID string for any incoming user_id.
    If it's already a UUID, keep it; otherwise, derive a stable UUIDv5.
    """
    try:
        return str(uuid.UUID(str(user_id)))
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"onb:{user_id}"))

def _save_profile_to_db(state: OBState) -> None:
    if not _sb:
        return
    p = state.get("profile", {}) or {}
    payload = {k: v for k, v in p.items() if k in _ALLOWED_DB_KEYS}
    if state.get("user_id"):
        payload["user_id"] = _to_uuid_str(state["user_id"])  # coerce to UUID
    try:
        _sb.table("profiles").upsert(payload, on_conflict="user_id").execute()
    except Exception as e:
        print(f"[supabase] upsert skipped: {e}")

def _display_name(state: OBState) -> str:
    return state.get("preferred_name") or state.get("user_name") or "صديقي"

# ---------- Nodes (Arabic, Saudi-friendly) ----------
def n_intro_name(state: OBState) -> Dict[str, Any]:
    msg = (
        "حياك الله! أنا *MORVO*، مستشارتك الذكية للتسويق في السوق السعودي 🇸🇦.\n"
        "أقدر أساعدك في تحليل الحملات، متابعة سمعة علامتك، تحسين الظهور في قوقل (SEO)، "
        "ووضع استراتيجيات تحقق عائد واضح.\n\n"
        "خلّينا نبدأ بالتعارف… وش *اسمك الأوّل*؟"
    )
    while True:
        val = ask(msg, ui_type="input")
        name = _clean_name(str(val))
        if name:
            return {"user_name": name}
        msg = "اسم غير واضح. اكتب *اسمك الأول* فقط (عربي/English مقبول)."

def n_preferred_choice(state: OBState) -> Dict[str, Any]:
    nm = state.get("user_name", "")
    choice = ask(
        f"تشرفنا يا *{nm}! تحب أناديك بـ **{nm}*؟",
        options=["إيّه، نفس الاسم", "أفضّل اسم مختلف"],
        ui_type="options",
    )
    return {"preferred_choice": str(choice)}

def n_preferred_input(state: OBState) -> Dict[str, Any]:
    nm = state.get("user_name", "")
    val = ask(f"اكتب *الاسم اللي تحب نناديك فيه* (أو اكتب {nm}):", ui_type="input")
    pn = _clean_name(str(val)) or nm
    return {"preferred_name": pn}

def n_role(state: OBState) -> Dict[str, Any]:
    val = ask("وش *دورك* في العمل؟",
              options=["مدير/ة تسويق", "مختص/ة تسويق", "مالك/ـة مشروع", "رائد/ة أعمال", "مدير/ة عام", "أخرى"],
              ui_type="options")
    prof = state.get("profile", {})
    prof["user_role"] = str(val)
    return {"profile": prof}

def n_industry(state: OBState) -> Dict[str, Any]:
    val = ask("نشاط شركتكم *إيش*؟ (مثال: تجارة إلكترونية، مطاعم، تعليم، تقنية…)", ui_type="input")
    prof = state.get("profile", {})
    prof["industry"] = str(val).strip()
    return {"profile": prof}

def n_company_size(state: OBState) -> Dict[str, Any]:
    val = ask("كم *حجم الشركة*؟",
              options=["👤 شخص واحد (فريلانسر)", "👥 2–10 موظفين", "🏢 11–50 موظف", "🏗 51+ موظف"],
              ui_type="options")
    prof = state.get("profile", {})
    prof["company_size"] = str(val)
    return {"profile": prof}

def n_website_status(state: OBState) -> Dict[str, Any]:
    val = ask("عندكم *موقع إلكتروني*؟",
              options=["✅ نعم – شغّال", "🔧 نعم – يحتاج تطوير", "🏗 تحت الإنشاء", "❌ لا"],
              ui_type="options")
    prof = state.get("profile", {})
    prof["website_status"] = "Yes" if str(val).startswith("✅") or str(val).startswith("🔧") else "No"
    return {"profile": prof}

def n_website_url(state: OBState) -> Dict[str, Any]:
    msg = "أرسل رابط الموقع (https://…)"
    while True:
        val = ask(msg, ui_type="input")
        url = _clean_url(str(val))
        if url:
            prof = state.get("profile", {})
            prof["website_url"] = url
            return {"profile": prof}
        msg = "الرابط غير صالح. مثال: https://example.com"

def n_goals(state: OBState) -> Dict[str, Any]:
    msg = "وش أهم *أهدافك التسويقية*؟ اكتبها مفصولة بفواصل (،). مثال: زيادة الوعي، تحسين التحويلات، ترتيب SEO…"
    val = ask(msg, ui_type="input")
    items = [x.strip() for x in re.split(r"[،,]", str(val)) if x.strip()]
    prof = state.get("profile", {})
    prof["primary_goals"] = items or []
    return {"profile": prof}

def n_budget(state: OBState) -> Dict[str, Any]:
    val = ask("كم تقريباً *ميزانيتكم الشهرية* للتسويق؟",
              options=["أقل من 5,000 ريال", "5,000–15,000 ريال", "15,000–50,000 ريال", "أكثر من 50,000 ريال", "حسب المشروع", "مو محددة"],
              ui_type="options")
    prof = state.get("profile", {})
    prof["budget_range"] = str(val)
    return {"profile": prof}

def n_save_and_finish(state: OBState) -> Dict[str, Any]:
    _save_profile_to_db(state)  # writes only allowed columns (safe no-op if sb not set)
    dn = _display_name(state)
    # final informational message (your FE can ignore; it's here for completeness)
    state["ui"] = {"ui_type": "input",
                   "message": f"تم يا *{dn}*! ✅ الآن اسألني أي شيء في التسويق وبعطيك توصيات عملية."}
    return {}

# ---------- Graph wiring ----------
_builder = StateGraph(OBState)
_builder.add_node("intro_name", n_intro_name)
_builder.add_node("preferred_choice", n_preferred_choice)
_builder.add_node("preferred_input", n_preferred_input)
_builder.add_node("role", n_role)
_builder.add_node("industry", n_industry)
_builder.add_node("company_size", n_company_size)
_builder.add_node("website_status", n_website_status)
_builder.add_node("website_url", n_website_url)
_builder.add_node("goals", n_goals)
_builder.add_node("budget", n_budget)
_builder.add_node("save", n_save_and_finish)

_builder.add_edge(START, "intro_name")
_builder.add_edge("intro_name", "preferred_choice")

def _branch_preferred(state: OBState) -> str:
    return "preferred_input" if state.get("preferred_choice") == "أفضّل اسم مختلف" else "role"

_builder.add_conditional_edges("preferred_choice", _branch_preferred, ["preferred_input", "role"])
_builder.add_edge("preferred_input", "role")
_builder.add_edge("role", "industry")
_builder.add_edge("industry", "company_size")
_builder.add_edge("company_size", "website_status")

def _branch_site(state: OBState) -> str:
    return "website_url" if state.get("profile", {}).get("website_status") == "Yes" else "goals"

_builder.add_conditional_edges("website_status", _branch_site, ["website_url", "goals"])
_builder.add_edge("website_url", "goals")
_builder.add_edge("goals", "budget")
_builder.add_edge("budget", "save")
_builder.add_edge("save", END)

_memory = InMemorySaver()
graph = _builder.compile(checkpointer=_memory)

# ---------- API helpers (used by main.py endpoints) ----------
def _cfg(user_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": f"onb:{user_id}"}}

def _current_ui(user_id: str) -> UIBlock:
    snap = graph.get_state(_cfg(user_id))
    vals = getattr(snap, "values", {}) or {}
    ui = vals.get("_interrupt_")
    if ui: return ui
    # fallback for older langgraph
    for t in getattr(snap, "tasks", []) or []:
        for intr in getattr(t, "interrupts", []) or []:
            if hasattr(intr, "value"): return intr.value
            if isinstance(intr, dict) and "value" in intr: return intr["value"]
    return {"ui_type": "input", "message": "…"}

def start_onboarding(user_id: str) -> Dict[str, Any]:
    initial: OBState = {"user_id": user_id, "profile": {}}
    graph.invoke(initial, _cfg(user_id))  # runs until first interrupt
    return {"conversation_id": f"onb:{user_id}", "done": False, "ui": _current_ui(user_id)}

def resume_onboarding(user_id: str, value: Any) -> Dict[str, Any]:
    graph.invoke(Command(resume=value), _cfg(user_id))
    snap = graph.get_state(_cfg(user_id))
    if snap.next is None:
        return {"conversation_id": f"onb:{user_id}", "done": True, "ui": None}
    return {"conversation_id": f"onb:{user_id}", "done": False, "ui": _current_ui(user_id)}