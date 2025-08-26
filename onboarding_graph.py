# onboarding_graph.py
from typing import TypedDict, Literal, Optional, List, Dict, Any, Annotated
from typing_extensions import NotRequired
import os, re, logging
from langgraph.graph import StateGraph, START, END
import uuid
from langgraph.types import Interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info("✅ Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Supabase init failed: {e}")
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

# ---------- Enhanced State Schema ----------
class UIBlock(TypedDict, total=False):
    ui_type: Literal["options", "input", "multi_select", "rating"]
    message: str
    options: NotRequired[List[str]]
    validation_rules: NotRequired[Dict[str, Any]]
    context: NotRequired[str]

class SessionState(TypedDict, total=False):
    # Core session data
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    
    # Onboarding state
    current_step: str
    step_data: Dict[str, Any]
    profile: Dict[str, Any]
    
    # UI state
    ui: UIBlock
    
    # Conversation history
    conversation_history: List[Dict[str, str]]
    
    # Error handling
    error_count: int
    last_error: Optional[str]
    
    # AI insights
    ai_insights: Optional[str]
    
    # Validation state
    validation_errors: List[str]

# ---------- AI Assistant with Retry Logic ----------
llm = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key,
            max_retries=3
        )
        logger.info("✅ OpenAI client initialized successfully")
    else:
        logger.warning("⚠️  OpenAI API key not found. AI features will be disabled.")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    llm = None

async def generate_smart_response_with_retry(context: str, user_input: str, profile_data: Dict[str, Any], max_retries: int = 3) -> str:
    """Generate contextual responses with retry logic"""
    if llm is None:
        return "شكراً لك! دعنا نكمل مع الخطوة التالية."
    
    for attempt in range(max_retries):
        try:
            system_prompt = f"""
            You are MORVO, a smart marketing assistant for the Saudi market. You're helping with user onboarding.
            
            Context: {context}
            Current Profile Data: {profile_data}
            User Input: {user_input}
            
            Respond in Arabic, be friendly and helpful. Provide personalized insights based on the user's profile.
            Keep responses concise but informative.
            """
            
            response = await llm.ainvoke([
                HumanMessage(content=f"Context: {context}\nProfile: {profile_data}\nUser: {user_input}")
            ])
            return response.content
            
        except Exception as e:
            logger.warning(f"AI response attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"All AI response attempts failed for context: {context}")
                return "شكراً لك! دعنا نكمل مع الخطوة التالية."
            await asyncio.sleep(1)  # Brief delay before retry

# ---------- Enhanced Validation Functions with Error Handling ----------
def validate_name(name: str) -> tuple[bool, str]:
    """Smart name validation with Arabic and Latin support"""
    try:
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
    except Exception as e:
        logger.error(f"Name validation error: {e}")
        return False, "حدث خطأ في التحقق من الاسم. حاول مرة أخرى"

def validate_url(url: str) -> tuple[bool, str]:
    """Smart URL validation with error handling"""
    try:
        url = url.strip()
        if not url:
            return False, "الرابط مطلوب"
        
        # Basic URL pattern
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if re.match(url_pattern, url, re.IGNORECASE):
            return True, url
        
        return False, "الرابط غير صحيح. مثال: https://example.com"
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return False, "حدث خطأ في التحقق من الرابط. حاول مرة أخرى"

def validate_goals(goals: str) -> tuple[bool, List[str]]:
    """Smart goals validation and parsing with error handling"""
    try:
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
    except Exception as e:
        logger.error(f"Goals validation error: {e}")
        return False, []

# ---------- Enhanced Onboarding Nodes with Session Management ----------
async def n_smart_intro(state: SessionState) -> SessionState:
    """Smart introduction with session management and error handling"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing intro step for user: {user_id}")
    
    try:
        # Update session activity
        state["last_activity"] = datetime.now()
        
        if "resume" in state.get("step_data", {}):
            user_input = str(state["step_data"]["resume"])
            is_valid, result = validate_name(user_input)
            
            if is_valid:
                # Generate personalized welcome
                profile_data = state.get("profile", {})
                profile_data["user_name"] = result
                
                welcome_msg = await generate_smart_response_with_retry(
                    "User provided their name during onboarding",
                    f"My name is {result}",
                    profile_data
                )
                
                state.update({
                    "profile": profile_data,
                    "ai_insights": welcome_msg,
                    "current_step": "role",
                    "step_data": {},
                    "validation_errors": []
                })
                
                logger.info(f"[{session_id}] Name validated successfully: {result}")
                return state
            else:
                # Handle validation error
                state.update({
                    "validation_errors": [result],
                    "error_count": state.get("error_count", 0) + 1
                })
                
                # Interrupt for invalid input
                raise Interrupt({
                    "ui_type": "input",
                    "message": f"❌ {result}\n\nحاول مرة أخرى. اكتب اسمك الأول فقط:",
                    "validation_rules": {"type": "name", "min_length": 2, "max_length": 40},
                    "context": "name_validation"
                })
        
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
        
        state.update({
            "current_step": "intro",
            "ui": {
                "ui_type": "input",
                "message": greeting,
                "validation_rules": {"type": "name", "min_length": 2, "max_length": 40},
                "context": "introduction"
            }
        })
        
        logger.info(f"[{session_id}] Intro step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in intro step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        # Return error state
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ. حاول مرة أخرى أو اكتب 'ابدأ' للبدء من جديد.",
            "context": "error_recovery"
        })

async def n_smart_role(state: SessionState) -> SessionState:
    """Smart role selection with session management"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing role step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        user_name = profile_data.get("user_name", "ضيفنا الكريم")
        
        # Personalized role options
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
        
        if "resume" in state.get("step_data", {}):
            selected_role = str(state["step_data"]["resume"])
            profile_data["user_role"] = selected_role
            
            # Generate role-specific insights
            role_insight = await generate_smart_response_with_retry(
                f"User selected role: {selected_role}",
                f"I am a {selected_role}",
                profile_data
            )
            
            state.update({
                "profile": profile_data,
                "ai_insights": role_insight,
                "current_step": "industry",
                "step_data": {},
                "validation_errors": []
            })
            
            logger.info(f"[{session_id}] Role selected: {selected_role}")
            return state
        
        message = f"تشرفنا يا {user_name}! 🎯\n\nوش دورك في العمل؟ اختر الدور الأقرب ليك:"
        
        state.update({
            "current_step": "role",
            "ui": {
                "ui_type": "options",
                "message": message,
                "options": role_options,
                "context": "role_selection"
            }
        })
        
        logger.info(f"[{session_id}] Role step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in role step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في اختيار الدور. حاول مرة أخرى.",
            "context": "error_recovery"
        })

# Continue with other nodes following the same pattern...
async def n_smart_industry(state: SessionState) -> SessionState:
    """Smart industry input with session management"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing industry step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        user_role = profile_data.get("user_role", "")
        
        if "resume" in state.get("step_data", {}):
            industry = str(state["step_data"]["resume"]).strip()
            if len(industry) < 3:
                state.update({
                    "validation_errors": ["النشاط قصير جداً"],
                    "error_count": state.get("error_count", 0) + 1
                })
                
                raise Interrupt({
                    "ui_type": "input",
                    "message": "❌ النشاط قصير جداً. اكتب نشاط شركتكم بالتفصيل:",
                    "validation_rules": {"min_length": 3, "max_length": 100},
                    "context": "industry_validation"
                })
            
            profile_data["industry"] = industry
            
            # Generate industry-specific insights
            industry_insight = await generate_smart_response_with_retry(
                f"User works in {industry} industry",
                f"My company is in {industry}",
                profile_data
            )
            
            state.update({
                "profile": profile_data,
                "ai_insights": industry_insight,
                "current_step": "company_size",
                "step_data": {},
                "validation_errors": []
            })
            
            logger.info(f"[{session_id}] Industry set: {industry}")
            return state
        
        # Industry suggestions based on role
        suggestions = {
            "👨‍💼 مدير/ة تسويق": "مثال: تجارة إلكترونية، مطاعم، تعليم، تقنية، خدمات مالية",
            "🎯 مختص/ة تسويق": "مثال: تسويق رقمي، إعلانات، علاقات عامة، تسويق مباشر",
            "💼 مالك/ـة مشروع": "مثال: تجارة، صناعة، خدمات، استشارات",
            "🚀 رائد/ة أعمال": "مثال: تقنية، تطبيقات، منصات رقمية، حلول مبتكرة"
        }
        
        suggestion = suggestions.get(user_role, "مثال: تجارة إلكترونية، مطاعم، تعليم، تقنية، خدمات مالية")
        message = f"🏢 نشاط شركتكم إيش؟\n\n{suggestion}"
        
        state.update({
            "current_step": "industry",
            "ui": {
                "ui_type": "input",
                "message": message,
                "validation_rules": {"min_length": 3, "max_length": 100},
                "context": "industry_input"
            }
        })
        
        logger.info(f"[{session_id}] Industry step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in industry step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في إدخال النشاط. حاول مرة أخرى.",
            "context": "error_recovery"
        })

# Add remaining nodes following the same pattern...
async def n_smart_company_size(state: SessionState) -> SessionState:
    """Smart company size selection"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing company size step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        
        if "resume" in state.get("step_data", {}):
            size = str(state["step_data"]["resume"])
            profile_data["company_size"] = size
            
            state.update({
                "profile": profile_data,
                "current_step": "website_status",
                "step_data": {},
                "validation_errors": []
            })
            
            logger.info(f"[{session_id}] Company size set: {size}")
            return state
        
        size_options = [
            "👤 شخص واحد (فريلانسر)",
            "👥 2–10 موظفين (شركة ناشئة)",
            "🏢 11–50 موظف (شركة متوسطة)",
            "🏗 51–200 موظف (شركة كبيرة)",
            "🏭 200+ موظف (شركة عملاقة)"
        ]
        
        message = "📊 كم حجم الشركة؟\n\nاختر الفئة الأقرب ليك:"
        
        state.update({
            "current_step": "company_size",
            "ui": {
                "ui_type": "options",
                "message": message,
                "options": size_options,
                "context": "company_size"
            }
        })
        
        logger.info(f"[{session_id}] Company size step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in company size step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في اختيار حجم الشركة. حاول مرة أخرى.",
            "context": "error_recovery"
        })

async def n_smart_website_status(state: SessionState) -> SessionState:
    """Smart website status with conditional logic"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing website status step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        
        if "resume" in state.get("step_data", {}):
            status = str(state["step_data"]["resume"])
            has_website = status.startswith("✅") or status.startswith("🔧")
            profile_data["website_status"] = "Yes" if has_website else "No"
            
            state.update({
                "profile": profile_data,
                "current_step": "website_url" if has_website else "goals",
                "step_data": {},
                "validation_errors": []
            })
            
            logger.info(f"[{session_id}] Website status set: {profile_data['website_status']}")
            return state
        
        status_options = [
            "✅ نعم – شغّال ومحسن",
            "🔧 نعم – يحتاج تطوير وتحسين",
            "🏗 تحت الإنشاء",
            "❌ لا، ما عندي موقع"
        ]
        
        message = "🌐 عندكم موقع إلكتروني؟\n\nاختر الحالة الأقرب ليك:"
        
        state.update({
            "current_step": "website_status",
            "ui": {
                "ui_type": "options",
                "message": message,
                "options": status_options,
                "context": "website_status"
            }
        })
        
        logger.info(f"[{session_id}] Website status step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in website status step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في اختيار حالة الموقع. حاول مرة أخرى.",
            "context": "error_recovery"
        })

async def n_smart_website_url(state: SessionState) -> SessionState:
    """Smart website URL validation"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing website URL step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        
        if "resume" in state.get("step_data", {}):
            url = str(state["step_data"]["resume"])
            is_valid, result = validate_url(url)
            
            if is_valid:
                profile_data["website_url"] = result
                
                state.update({
                    "profile": profile_data,
                    "current_step": "goals",
                    "step_data": {},
                    "validation_errors": []
                })
                
                logger.info(f"[{session_id}] Website URL set: {result}")
                return state
            else:
                state.update({
                    "validation_errors": [result],
                    "error_count": state.get("error_count", 0) + 1
                })
                
                raise Interrupt({
                    "ui_type": "input",
                    "message": f"❌ {result}\n\nحاول مرة أخرى:",
                    "validation_rules": {"type": "url"},
                    "context": "url_validation"
                })
        
        message = "🔗 أرسل رابط الموقع\n\nمثال: https://example.com"
        
        state.update({
            "current_step": "website_url",
            "ui": {
                "ui_type": "input",
                "message": message,
                "validation_rules": {"type": "url"},
                "context": "website_url"
            }
        })
        
        logger.info(f"[{session_id}] Website URL step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in website URL step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في إدخال رابط الموقع. حاول مرة أخرى.",
            "context": "error_recovery"
        })

async def n_smart_goals(state: SessionState) -> SessionState:
    """Smart goals collection with suggestions"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing goals step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        industry = profile_data.get("industry", "")
        
        if "resume" in state.get("step_data", {}):
            goals_input = str(state["step_data"]["resume"])
            is_valid, goals_list = validate_goals(goals_input)
            
            if is_valid:
                profile_data["primary_goals"] = goals_list
                
                # Generate goals-specific insights
                goals_insight = await generate_smart_response_with_retry(
                    f"User goals: {', '.join(goals_list)}",
                    f"My marketing goals are: {goals_input}",
                    profile_data
                )
                
                state.update({
                    "profile": profile_data,
                    "ai_insights": goals_insight,
                    "current_step": "budget",
                    "step_data": {},
                    "validation_errors": []
                })
                
                logger.info(f"[{session_id}] Goals set: {goals_list}")
                return state
            else:
                state.update({
                    "validation_errors": ["الأهداف غير واضحة"],
                    "error_count": state.get("error_count", 0) + 1
                })
                
                raise Interrupt({
                    "ui_type": "input",
                    "message": "❌ الأهداف غير واضحة. اكتب أهدافك مفصولة بفواصل:",
                    "validation_rules": {"min_length": 5},
                    "context": "goals_validation"
                })
        
        # Industry-specific goal suggestions
        goal_suggestions = {
            "تجارة إلكترونية": "زيادة المبيعات، تحسين التحويلات، توسيع قاعدة العملاء",
            "مطاعم": "زيادة الطلبات، تحسين تجربة العملاء، التوسع الجغرافي",
            "تعليم": "زيادة التسجيلات، تحسين المحتوى التعليمي، بناء السمعة",
            "تقنية": "زيادة المستخدمين، تحسين المنتج، التوسع في السوق"
        }
        
        suggestion = goal_suggestions.get(industry, "زيادة الوعي، تحسين التحويلات، ترتيب SEO، بناء السمعة")
        message = f"🎯 وش أهم أهدافك التسويقية؟\n\nاكتبها مفصولة بفواصل (،)\nمثال: {suggestion}"
        
        state.update({
            "current_step": "goals",
            "ui": {
                "ui_type": "input",
                "message": message,
                "validation_rules": {"min_length": 5, "max_length": 200},
                "context": "goals_input"
            }
        })
        
        logger.info(f"[{session_id}] Goals step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in goals step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في إدخال الأهداف. حاول مرة أخرى.",
            "context": "error_recovery"
        })

async def n_smart_budget(state: SessionState) -> SessionState:
    """Smart budget selection with recommendations"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Processing budget step for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        company_size = profile_data.get("company_size", "")
        
        if "resume" in state.get("step_data", {}):
            budget = str(state["step_data"]["resume"])
            profile_data["budget_range"] = budget
            
            state.update({
                "profile": profile_data,
                "current_step": "complete",
                "step_data": {},
                "validation_errors": []
            })
            
            logger.info(f"[{session_id}] Budget set: {budget}")
            return state
        
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
        
        state.update({
            "current_step": "budget",
            "ui": {
                "ui_type": "options",
                "message": message,
                "options": budget_options,
                "context": "budget_selection"
            }
        })
        
        logger.info(f"[{session_id}] Budget step completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error in budget step: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        raise Interrupt({
            "ui_type": "input",
            "message": "عذراً، حدث خطأ في اختيار الميزانية. حاول مرة أخرى.",
            "context": "error_recovery"
        })

async def n_complete_onboarding(state: SessionState) -> SessionState:
    """Complete onboarding with personalized summary and database save"""
    session_id = state.get("session_id")
    user_id = state.get("user_id")
    
    logger.info(f"[{session_id}] Completing onboarding for user: {user_id}")
    
    try:
        state["last_activity"] = datetime.now()
        profile_data = state.get("profile", {})
        user_name = profile_data.get("user_name", "ضيفنا الكريم")
        
        # Save to database with retry logic
        await _save_profile_to_db_with_retry(state)
        
        # Generate personalized completion message
        completion_msg = await generate_smart_response_with_retry(
            "Onboarding completed successfully",
            f"Profile completed for {user_name}",
            profile_data
        )
        
        final_message = f"تم يا {user_name}! ✅\n\n{completion_msg}\n\n🎉 الآن اسألني أي شيء في التسويق وبعطيك توصيات عملية ومخصصة ليك!"
        
        state.update({
            "current_step": "complete",
            "ui": {
                "ui_type": "input",
                "message": final_message,
                "context": "completion"
            },
            "validation_errors": []
        })
        
        logger.info(f"[{session_id}] Onboarding completed successfully for user: {user_id}")
        return state
        
    except Exception as e:
        logger.error(f"[{session_id}] Error completing onboarding: {e}")
        state.update({
            "last_error": str(e),
            "error_count": state.get("error_count", 0) + 1
        })
        
        # Even if save fails, complete the onboarding
        final_message = f"تم يا {user_name}! ✅\n\n🎉 الآن اسألني أي شيء في التسويق وبعطيك توصيات عملية ومخصصة ليك!"
        
        state.update({
            "current_step": "complete",
            "ui": {
                "ui_type": "input",
                "message": final_message,
                "context": "completion"
            }
        })
        
        return state

# ---------- Enhanced Graph with Session Management ----------
def create_enhanced_onboarding_graph():
    """Create the enhanced onboarding graph with session management"""
    builder = StateGraph(SessionState)
    
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
    def route_after_website_status(state: SessionState) -> str:
        has_website = state.get("profile", {}).get("website_status") == "Yes"
        return "website_url" if has_website else "goals"
    
    builder.add_conditional_edges("website_status", route_after_website_status, ["website_url", "goals"])
    builder.add_edge("website_url", "goals")
    builder.add_edge("goals", "budget")
    builder.add_edge("budget", "complete")
    builder.add_edge("complete", END)
    
    # Configure interrupts for user input
    builder.set_interrupt_before(["intro", "role", "industry", "company_size", "website_status", "website_url", "goals", "budget"])
    
    return builder.compile(checkpointer=InMemorySaver())

# Create enhanced graph instance
enhanced_graph = create_enhanced_onboarding_graph()

# ---------- Enhanced Helper Functions ----------
def _to_uuid_str(user_id: str) -> str:
    """Return a valid UUID string for any incoming user_id."""
    try:
        return str(uuid.UUID(str(user_id)))
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"onb:{user_id}"))

async def _save_profile_to_db_with_retry(state: SessionState, max_retries: int = 3) -> None:
    """Save profile data to Supabase with retry logic"""
    if not _sb:
        logger.warning(f"[{state.get('session_id')}] Supabase not available, skipping save")
        return
    
    session_id = state.get("session_id")
    
    for attempt in range(max_retries):
        try:
            profile_data = state.get("profile", {})
            payload = {k: v for k, v in profile_data.items() if k in _ALLOWED_DB_KEYS}
            
            # Ensure user_id is always set
            user_id = state.get("user_id")
            if user_id:
                payload["user_id"] = _to_uuid_str(user_id)
            else:
                logger.error(f"[{session_id}] No user_id in state, skipping save")
                return
            
            logger.info(f"[{session_id}] Saving profile (attempt {attempt + 1}): {payload}")
            _sb.table("profiles").upsert(payload, on_conflict="user_id").execute()
            logger.info(f"[{session_id}] Profile saved successfully for user: {user_id}")
            return
            
        except Exception as e:
            logger.warning(f"[{session_id}] Profile save attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"[{session_id}] All profile save attempts failed")
                raise
            await asyncio.sleep(1)  # Brief delay before retry

def _cfg(session_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": f"onb:{session_id}"}}

def _current_ui(session_id: str) -> UIBlock:
    """Get current UI state from enhanced graph"""
    try:
        snap = enhanced_graph.get_state(_cfg(session_id))
        vals = getattr(snap, "values", {}) or {}
        
        # Check for interrupt state
        ui = vals.get("_interrupt_")
        if ui:
            return ui
        
        # Check for UI in state values
        ui = vals.get("ui")
        if ui:
            return ui
        
        # Fallback for older langgraph
        for t in getattr(snap, "tasks", []) or []:
            for intr in getattr(t, "interrupts", []) or []:
                if hasattr(intr, "value"):
                    return intr.value
                if isinstance(intr, dict) and "value" in intr:
                    return intr["value"]
        
        # If no UI found, return a proper greeting message
        return {
            "ui_type": "input", 
            "message": "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق في السوق السعودي 🇸🇦\n\nخلّينا نبدأ بالتعارف… وش اسمك الأول؟"
        }
    except Exception as e:
        logger.error(f"[{session_id}] Error getting UI state: {e}")
        return {
            "ui_type": "input", 
            "message": "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق في السوق السعودي 🇸🇦\n\nخلّينا نبدأ بالتعارف… وش اسمك الأول؟"
        }

# ---------- Enhanced API Functions with Session Management ----------
async def start_enhanced_onboarding(user_id: str) -> Dict[str, Any]:
    """Start the enhanced onboarding process with session management"""
    session_id = f"onb_{user_id}_{int(datetime.now().timestamp())}"
    
    initial: SessionState = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.now(),
        "last_activity": datetime.now(),
        "profile": {},
        "conversation_history": [],
        "current_step": "intro",
        "step_data": {},
        "error_count": 0,
        "validation_errors": []
    }
    
    logger.info(f"[{session_id}] Starting enhanced onboarding for user: {user_id}")
    
    try:
        await enhanced_graph.ainvoke(initial, _cfg(session_id))
        
        return {
            "session_id": session_id,
            "conversation_id": f"onb:{user_id}",
            "done": False,
            "ui": _current_ui(session_id)
        }
    except Exception as e:
        logger.error(f"[{session_id}] Error starting onboarding: {e}")
        return {
            "session_id": session_id,
            "conversation_id": f"onb:{user_id}",
            "done": False,
            "ui": {
                "ui_type": "input",
                "message": "عذراً، حدث خطأ في بدء التسجيل. حاول مرة أخرى.",
                "context": "error_recovery"
            }
        }

async def resume_enhanced_onboarding(session_id: str, value: Any) -> Dict[str, Any]:
    """Resume enhanced onboarding with user input and session management"""
    logger.info(f"[{session_id}] Resuming enhanced onboarding with value: {value}")
    
    try:
        await enhanced_graph.ainvoke({"step_data": {"resume": value}}, _cfg(session_id))
        snap = enhanced_graph.get_state(_cfg(session_id))
        
        if snap.next is None:
            logger.info(f"[{session_id}] Enhanced onboarding completed")
            return {
                "session_id": session_id,
                "conversation_id": f"onb:{session_id}",
                "done": True,
                "ui": None
            }
        
        return {
            "session_id": session_id,
            "conversation_id": f"onb:{session_id}",
            "done": False,
            "ui": _current_ui(session_id)
        }
    except Exception as e:
        logger.error(f"[{session_id}] Error resuming onboarding: {e}")
        return {
            "session_id": session_id,
            "conversation_id": f"onb:{session_id}",
            "done": False,
            "ui": {
                "ui_type": "input",
                "message": "عذراً، حدث خطأ في معالجة إجابتك. حاول مرة أخرى.",
                "context": "error_recovery"
            }
        }

# ---------- Backward Compatibility Functions ----------
def start_onboarding(user_id: str) -> Dict[str, Any]:
    """Backward compatibility wrapper for start_onboarding"""
    import asyncio
    try:
        return asyncio.run(start_enhanced_onboarding(user_id))
    except Exception as e:
        logger.error(f"Error in start_onboarding: {e}")
        return {
            "conversation_id": f"onb:{user_id}",
            "done": False,
            "ui": {
                "ui_type": "input",
                "message": "حياك الله! أنا MORVO 🤝 مستشارتك الذكية للتسويق في السوق السعودي 🇸🇦\n\nخلّينا نبدأ بالتعارف… وش اسمك الأول؟"
            }
        }

def resume_onboarding(user_id: str, value: Any) -> Dict[str, Any]:
    """Backward compatibility wrapper for resume_onboarding"""
    import asyncio
    try:
        # Try to get session_id from existing state
        session_id = f"onb_{user_id}_legacy"
        return asyncio.run(resume_enhanced_onboarding(session_id, value))
    except Exception as e:
        logger.error(f"Error in resume_onboarding: {e}")
        return {
            "conversation_id": f"onb:{user_id}",
            "done": False,
            "ui": {
                "ui_type": "input",
                "message": "عذراً، حدث خطأ. حاول مرة أخرى.",
                "context": "error_recovery"
            }
        }

# Legacy functions for backward compatibility
def _save_profile_to_db(state: Dict[str, Any]) -> None:
    """Legacy save function for backward compatibility"""
    import asyncio
    try:
        session_state = SessionState(
            session_id="legacy",
            user_id=state.get("user_id", ""),
            created_at=datetime.now(),
            last_activity=datetime.now(),
            profile=state.get("profile", {}),
            current_step="",
            step_data={},
            conversation_history=[],
            error_count=0,
            validation_errors=[]
        )
        asyncio.run(_save_profile_to_db_with_retry(session_state))
    except Exception as e:
        logger.error(f"Legacy save failed: {e}")

# Create legacy graph instance for backward compatibility
graph = enhanced_graph