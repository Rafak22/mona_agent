# onboarding_graph.py
from typing import TypedDict, Literal, Optional, List, Dict, Any, Annotated
from typing_extensions import NotRequired
import os, re
from langgraph.graph import StateGraph, START, END
import uuid
from langgraph.types import Interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

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
    "marketing_experience",
    "target_audience",
    "current_challenges",
}

# ---------- State schema ----------
class UIBlock(TypedDict, total=False):
    ui_type: Literal["options", "input", "multi_select", "rating"]
    message: str
    options: NotRequired[List[str]]
    validation_rules: NotRequired[Dict[str, Any]]
    context: NotRequired[str]

class OBState(TypedDict, total=False):
    user_id: str
    profile: Dict[str, Any]        # holds the DB fields listed above
    ui: UIBlock
    user_name: Optional[str]
    preferred_name: Optional[str]
    preferred_choice: Optional[str]
    conversation_history: List[Dict[str, str]]
    current_step: str
    step_data: Dict[str, Any]
    ai_insights: Optional[str]

# ---------- AI Assistant for Smart Responses ----------
llm = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key
        )
    else:
        print("⚠️  OpenAI API key not found. AI features will be disabled.")
except Exception as e:
    print(f"⚠️  Failed to initialize OpenAI client: {e}")
    llm = None

def generate_smart_response(context: str, user_input: str, profile_data: Dict[str, Any]) -> str:
    """Generate contextual responses based on user input and profile data"""
    if llm is None:
        return "شكراً لك! دعنا نكمل مع الخطوة التالية."
    
    system_prompt = f"""
    You are MORVO, a smart marketing assistant for the Saudi market. You're helping with user onboarding.
    
    Context: {context}
    Current Profile Data: {profile_data}
    User Input: {user_input}
    
    Respond in Arabic, be friendly and helpful. Provide personalized insights based on the user's profile.
    Keep responses concise but informative.
    """
    
    try:
        response = llm.invoke([
            HumanMessage(content=f"Context: {context}\nProfile: {profile_data}\nUser: {user_input}")
        ])
        return response.content
    except Exception as e:
        print(f"[AI] Error generating response: {e}")
        return "شكراً لك! دعنا نكمل مع الخطوة التالية."

# ---------- Smart Validation Functions ----------
def validate_name(name: str) -> tuple[bool, str]:
    """Smart name validation with Arabic and Latin support"""
    name = name.strip()
    if not name:
        return False, "الاسم مطلوب"
    
    # Check for common non-name responses
    non_names = {"ايه", "أيه", "ايوه", "أيوه", "نعم", "لا", "تمام", "طيب", "اوكي", "أوكي", "اوكيه",
                "مرحبا", "اهلا", "أهلا", "هلا", "thanks", "thank you", "ok", "okay", "hello", "hi"}
    
    if name.lower() in non_names:
        return False, "هذا ليس اسماً. يرجى كتابة اسمك الأول"
    
    # Arabic name pattern
    arabic_pattern = r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s\-']{2,40}$"
    # Latin name pattern
    latin_pattern = r"^[A-Za-z\s\-']{2,40}$"
    
    if re.match(arabic_pattern, name) or re.match(latin_pattern, name):
        return True, name.title() if name.isascii() else name
    
    return False, "الاسم غير صحيح. يرجى كتابة اسم صحيح"

def validate_url(url: str) -> tuple[bool, str]:
    """Smart URL validation"""
    url = url.strip()
    if not url:
        return False, "الرابط مطلوب"
    
    # Basic URL pattern
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if re.match(url_pattern, url, re.IGNORECASE):
        return True, url
    
    return False, "الرابط غير صحيح. مثال: https://example.com"

def validate_goals(goals: str) -> tuple[bool, List[str]]:
    """Smart goals validation and parsing"""
    goals = goals.strip()
    if not goals:
        return False, []
    
    # Split by common separators
    goal_list = [g.strip() for g in re.split(r"[،,;]", goals) if g.strip()]
    
    if len(goal_list) < 1:
        return False, []
    
    if len(goal_list) > 5:
        return False, goal_list[:5]  # Limit to 5 goals
    
    return True, goal_list

# ---------- Smart Onboarding Nodes ----------
def n_smart_intro(state: OBState) -> Dict[str, Any]:
    """Smart introduction with personalized greeting"""
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        user_input = str(state["resume"])
        is_valid, result = validate_name(user_input)
        
        if is_valid:
            # Generate personalized welcome
            profile_data = state.get("profile", {})
            profile_data["user_name"] = result
            welcome_msg = generate_smart_response(
                "User provided their name during onboarding",
                f"My name is {result}",
                profile_data
            )
            
            return {
                "user_id": user_id,  # Preserve user_id
                "user_name": result,
                "profile": profile_data,
                "ai_insights": welcome_msg,
                "current_step": "role"
            }
        else:
            return {
                "user_id": user_id,  # Preserve user_id
                "ui": {
                    "ui_type": "input",
                    "message": f"❌ {result}\n\nحاول مرة أخرى. اكتب اسمك الأول فقط:",
                    "validation_rules": {"type": "name", "min_length": 2, "max_length": 40},
                    "context": "name_validation"
                }
            }
    
    # First time greeting
    greeting = (
        "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق في السوق السعودي 🇸🇦\n\n"
        "أقدر أساعدك في:\n"
        "• تحليل الحملات التسويقية 📊\n"
        "• متابعة سمعة علامتك التجارية 🏢\n"
        "• تحسين الظهور في محركات البحث (SEO) 🔍\n"
        "• وضع استراتيجيات تحقق عائد واضح 💰\n\n"
        "خلّينا نبدأ بالتعارف… وش اسمك الأول؟"
    )
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "input",
            "message": greeting,
            "validation_rules": {"type": "name", "min_length": 2, "max_length": 40},
            "context": "introduction"
        },
        "current_step": "intro"
    }

def n_smart_role(state: OBState) -> Dict[str, Any]:
    """Smart role selection with contextual options"""
    profile_data = state.get("profile", {})
    user_name = profile_data.get("user_name", "ضيفنا الكريم")
    user_id = state.get("user_id")  # Preserve user_id
    
    # Personalized role options based on context
    role_options = [
        "👨‍💼 مدير/ة تسويق",
        "🎯 مختص/ة تسويق",
        "💼 مالك/ـة مشروع",
        "🚀 رائد/ة أعمال",
        "🏢 مدير/ة عام",
        "📈 محلل/ة بيانات",
        "🎨 مصمم/ة إبداعي",
        "أخرى"
    ]
    
    if "resume" in state:
        selected_role = str(state["resume"])
        profile_data["user_role"] = selected_role
        
        # Generate role-specific insights
        role_insight = generate_smart_response(
            f"User selected role: {selected_role}",
            f"I am a {selected_role}",
            profile_data
        )
        
        return {
            "user_id": user_id,  # Preserve user_id
            "profile": profile_data,
            "ai_insights": role_insight,
            "current_step": "industry"
        }
    
    message = f"تشرفنا يا {user_name}! 🎯\n\nوش دورك في العمل؟ اختر الدور الأقرب ليك:"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "options",
            "message": message,
            "options": role_options,
            "context": "role_selection"
        },
        "current_step": "role"
    }

def n_smart_industry(state: OBState) -> Dict[str, Any]:
    """Smart industry input with suggestions"""
    profile_data = state.get("profile", {})
    user_role = profile_data.get("user_role", "")
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        industry = str(state["resume"]).strip()
        if len(industry) < 3:
            return {
                "user_id": user_id,  # Preserve user_id
                "ui": {
                    "ui_type": "input",
                    "message": "❌ النشاط قصير جداً. اكتب نشاط شركتكم بالتفصيل:",
                    "validation_rules": {"min_length": 3, "max_length": 100},
                    "context": "industry_validation"
                }
            }
        
        profile_data["industry"] = industry
        
        # Generate industry-specific insights
        industry_insight = generate_smart_response(
            f"User works in {industry} industry",
            f"My company is in {industry}",
            profile_data
        )
        
        return {
            "user_id": user_id,  # Preserve user_id
            "profile": profile_data,
            "ai_insights": industry_insight,
            "current_step": "company_size"
        }
    
    # Industry suggestions based on role
    suggestions = {
        "👨‍💼 مدير/ة تسويق": "مثال: تجارة إلكترونية، مطاعم، تعليم، تقنية، خدمات مالية",
        "🎯 مختص/ة تسويق": "مثال: تسويق رقمي، إعلانات، علاقات عامة، تسويق مباشر",
        "💼 مالك/ـة مشروع": "مثال: تجارة، صناعة، خدمات، استشارات",
        "🚀 رائد/ة أعمال": "مثال: تقنية، تطبيقات، منصات رقمية، حلول مبتكرة"
    }
    
    suggestion = suggestions.get(user_role, "مثال: تجارة إلكترونية، مطاعم، تعليم، تقنية، خدمات مالية")
    
    message = f"🏢 نشاط شركتكم إيش؟\n\n{suggestion}"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "input",
            "message": message,
            "validation_rules": {"min_length": 3, "max_length": 100},
            "context": "industry_input"
        },
        "current_step": "industry"
    }

def n_smart_company_size(state: OBState) -> Dict[str, Any]:
    """Smart company size selection"""
    profile_data = state.get("profile", {})
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        size = str(state["resume"])
        profile_data["company_size"] = size
        return {
            "user_id": user_id,  # Preserve user_id
            "profile": profile_data,
            "current_step": "website_status"
        }
    
    size_options = [
        "👤 شخص واحد (فريلانسر)",
        "👥 2–10 موظفين (شركة ناشئة)",
        "🏢 11–50 موظف (شركة متوسطة)",
        "🏗 51–200 موظف (شركة كبيرة)",
        "🏭 200+ موظف (شركة عملاقة)"
    ]
    
    message = "📊 كم حجم الشركة؟\n\nاختر الفئة الأقرب ليك:"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "options",
            "message": message,
            "options": size_options,
            "context": "company_size"
        },
        "current_step": "company_size"
    }

def n_smart_website_status(state: OBState) -> Dict[str, Any]:
    """Smart website status with conditional logic"""
    profile_data = state.get("profile", {})
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        status = str(state["resume"])
        has_website = status.startswith("✅") or status.startswith("🔧")
        profile_data["website_status"] = "Yes" if has_website else "No"
        
        return {
            "user_id": user_id,  # Preserve user_id
            "profile": profile_data,
            "current_step": "website_url" if has_website else "goals"
        }
    
    status_options = [
        "✅ نعم – شغّال ومحسن",
        "🔧 نعم – يحتاج تطوير وتحسين",
        "🏗 تحت الإنشاء",
        "❌ لا، ما عندي موقع"
    ]
    
    message = "🌐 عندكم موقع إلكتروني؟\n\nاختر الحالة الأقرب ليك:"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "options",
            "message": message,
            "options": status_options,
            "context": "website_status"
        },
        "current_step": "website_status"
    }

def n_smart_website_url(state: OBState) -> Dict[str, Any]:
    """Smart website URL validation"""
    profile_data = state.get("profile", {})
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        url = str(state["resume"])
        is_valid, result = validate_url(url)
        
        if is_valid:
            profile_data["website_url"] = result
            return {
                "user_id": user_id,  # Preserve user_id
                "profile": profile_data,
                "current_step": "goals"
            }
        else:
            return {
                "user_id": user_id,  # Preserve user_id
                "ui": {
                    "ui_type": "input",
                    "message": f"❌ {result}\n\nحاول مرة أخرى:",
                    "validation_rules": {"type": "url"},
                    "context": "url_validation"
                }
            }
    
    message = "🔗 أرسل رابط الموقع\n\nمثال: https://example.com"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "input",
            "message": message,
            "validation_rules": {"type": "url"},
            "context": "website_url"
        },
        "current_step": "website_url"
    }

def n_smart_goals(state: OBState) -> Dict[str, Any]:
    """Smart goals collection with suggestions"""
    profile_data = state.get("profile", {})
    industry = profile_data.get("industry", "")
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        goals_input = str(state["resume"])
        is_valid, goals_list = validate_goals(goals_input)
        
        if is_valid:
            profile_data["primary_goals"] = goals_list
            
            # Generate goals-specific insights
            goals_insight = generate_smart_response(
                f"User goals: {', '.join(goals_list)}",
                f"My marketing goals are: {goals_input}",
                profile_data
            )
            
            return {
                "user_id": user_id,  # Preserve user_id
                "profile": profile_data,
                "ai_insights": goals_insight,
                "current_step": "budget"
            }
        else:
            return {
                "user_id": user_id,  # Preserve user_id
                "ui": {
                    "ui_type": "input",
                    "message": "❌ الأهداف غير واضحة. اكتب أهدافك مفصولة بفواصل:",
                    "validation_rules": {"min_length": 5},
                    "context": "goals_validation"
                }
            }
    
    # Industry-specific goal suggestions
    goal_suggestions = {
        "تجارة إلكترونية": "زيادة المبيعات، تحسين التحويلات، توسيع قاعدة العملاء",
        "مطاعم": "زيادة الطلبات، تحسين تجربة العملاء، التوسع الجغرافي",
        "تعليم": "زيادة التسجيلات، تحسين المحتوى التعليمي، بناء السمعة",
        "تقنية": "زيادة المستخدمين، تحسين المنتج، التوسع في السوق"
    }
    
    suggestion = goal_suggestions.get(industry, "زيادة الوعي، تحسين التحويلات، ترتيب SEO، بناء السمعة")
    
    message = f"🎯 وش أهم أهدافك التسويقية؟\n\nاكتبها مفصولة بفواصل (،)\nمثال: {suggestion}"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "input",
            "message": message,
            "validation_rules": {"min_length": 5, "max_length": 200},
            "context": "goals_input"
        },
        "current_step": "goals"
    }

def n_smart_budget(state: OBState) -> Dict[str, Any]:
    """Smart budget selection with recommendations"""
    profile_data = state.get("profile", {})
    company_size = profile_data.get("company_size", "")
    user_id = state.get("user_id")  # Preserve user_id
    
    if "resume" in state:
        budget = str(state["resume"])
        profile_data["budget_range"] = budget
        return {
            "user_id": user_id,  # Preserve user_id
            "profile": profile_data,
            "current_step": "complete"
        }
    
    # Budget options based on company size
    if "شخص واحد" in company_size:
        budget_options = [
            "أقل من 1,000 ريال",
            "1,000–3,000 ريال",
            "3,000–5,000 ريال",
            "أكثر من 5,000 ريال"
        ]
    elif "2–10" in company_size:
        budget_options = [
            "أقل من 5,000 ريال",
            "5,000–15,000 ريال",
            "15,000–30,000 ريال",
            "أكثر من 30,000 ريال"
        ]
    else:
        budget_options = [
            "أقل من 10,000 ريال",
            "10,000–25,000 ريال",
            "25,000–50,000 ريال",
            "أكثر من 50,000 ريال",
            "حسب المشروع",
            "مو محددة"
        ]
    
    message = "💰 كم تقريباً ميزانيتكم الشهرية للتسويق؟\n\nاختر الفئة المناسبة:"
    
    return {
        "ui": {
            "ui_type": "options",
            "message": message,
            "options": budget_options,
            "context": "budget_selection"
        },
        "current_step": "budget"
    }

def n_complete_onboarding(state: OBState) -> Dict[str, Any]:
    """Complete onboarding with personalized summary"""
    profile_data = state.get("profile", {})
    user_name = profile_data.get("user_name", "ضيفنا الكريم")
    user_id = state.get("user_id")  # Preserve user_id
    
    # Save to database
    _save_profile_to_db(state)
    
    # Generate personalized completion message
    completion_msg = generate_smart_response(
        "Onboarding completed successfully",
        f"Profile completed for {user_name}",
        profile_data
    )
    
    final_message = f"تم يا {user_name}! ✅\n\n{completion_msg}\n\n🎉 الآن اسألني أي شيء في التسويق وبعطيك توصيات عملية ومخصصة ليك!"
    
    return {
        "user_id": user_id,  # Preserve user_id
        "ui": {
            "ui_type": "input",
            "message": final_message,
            "context": "completion"
        },
        "current_step": "complete"
    }

# ---------- Graph wiring ----------
def create_onboarding_graph():
    """Create the smart onboarding graph"""
    builder = StateGraph(OBState)
    
    # Add nodes
    builder.add_node("intro", n_smart_intro)
    builder.add_node("role", n_smart_role)
    builder.add_node("industry", n_smart_industry)
    builder.add_node("company_size", n_smart_company_size)
    builder.add_node("website_status", n_smart_website_status)
    builder.add_node("website_url", n_smart_website_url)
    builder.add_node("goals", n_smart_goals)
    builder.add_node("budget", n_smart_budget)
    builder.add_node("complete", n_complete_onboarding)
    
    # Add edges
    builder.add_edge(START, "intro")
    builder.add_edge("intro", "role")
    builder.add_edge("role", "industry")
    builder.add_edge("industry", "company_size")
    builder.add_edge("company_size", "website_status")
    
    # Conditional edges
    def route_after_website_status(state: OBState) -> str:
        has_website = state.get("profile", {}).get("website_status") == "Yes"
        return "website_url" if has_website else "goals"
    
    builder.add_conditional_edges("website_status", route_after_website_status, ["website_url", "goals"])
    builder.add_edge("website_url", "goals")
    builder.add_edge("goals", "budget")
    builder.add_edge("budget", "complete")
    builder.add_edge("complete", END)
    
    return builder.compile(checkpointer=InMemorySaver())

# Create graph instance
graph = create_onboarding_graph()

# ---------- Helper functions ----------
def _to_uuid_str(user_id: str) -> str:
    """Return a valid UUID string for any incoming user_id."""
    try:
        return str(uuid.UUID(str(user_id)))
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"onb:{user_id}"))

def _save_profile_to_db(state: OBState) -> None:
    """Save profile data to Supabase"""
    if not _sb:
        print(f"[onboarding] Supabase not available, skipping save")
        return
    
    try:
        profile_data = state.get("profile", {})
        payload = {k: v for k, v in profile_data.items() if k in _ALLOWED_DB_KEYS}
        
        # Ensure user_id is always set
        user_id = state.get("user_id")
        if user_id:
            payload["user_id"] = _to_uuid_str(user_id)
        else:
            print(f"[onboarding] No user_id in state, skipping save")
            return
        
        print(f"[onboarding] saving profile: {payload}")
        _sb.table("profiles").upsert(payload, on_conflict="user_id").execute()
        print(f"[onboarding] saved profile for {user_id} -> {payload.get('user_id')}")
    except Exception as e:
        print(f"[onboarding] failed to save profile: {e}")
        print(f"[onboarding] payload was: {payload}")

def _cfg(user_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": f"onb:{user_id}"}}

def _current_ui(user_id: str) -> UIBlock:
    """Get current UI state from graph"""
    snap = graph.get_state(_cfg(user_id))
    vals = getattr(snap, "values", {}) or {}
    ui = vals.get("_interrupt_")
    if ui:
        return ui
    
    # Fallback for older langgraph
    for t in getattr(snap, "tasks", []) or []:
        for intr in getattr(t, "interrupts", []) or []:
            if hasattr(intr, "value"):
                return intr.value
            if isinstance(intr, dict) and "value" in intr:
                return intr["value"]
    
    return {"ui_type": "input", "message": "…"}

# ---------- API functions ----------
def start_onboarding(user_id: str) -> Dict[str, Any]:
    """Start the smart onboarding process"""
    initial: OBState = {
        "user_id": user_id,
        "profile": {},
        "conversation_history": [],
        "current_step": "intro",
        "step_data": {}
    }
    
    print(f"[onboarding] starting smart onboarding for user_id: {user_id}")
    graph.invoke(initial, _cfg(user_id))
    
    return {
        "conversation_id": f"onb:{user_id}",
        "done": False,
        "ui": _current_ui(user_id)
    }

def resume_onboarding(user_id: str, value: Any) -> Dict[str, Any]:
    """Resume onboarding with user input"""
    print(f"[onboarding] resuming smart onboarding for user_id: {user_id} with value: {value}")
    
    graph.invoke({"resume": value}, _cfg(user_id))
    snap = graph.get_state(_cfg(user_id))
    
    if snap.next is None:
        print(f"[onboarding] smart onboarding completed for user_id: {user_id}")
        return {
            "conversation_id": f"onb:{user_id}",
            "done": True,
            "ui": None
        }
    
    return {
        "conversation_id": f"onb:{user_id}",
        "done": False,
        "ui": _current_ui(user_id)
    }