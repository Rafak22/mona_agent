import re
import uuid
import os
from typing import Dict, Any, Optional, List
from enum import Enum

# Supabase integration
try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
_sb: Optional["Client"] = None

if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        _sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"[onboarding] Supabase connected")
    except Exception as e:
        print(f"[onboarding] Supabase init failed: {e}")
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

# Simple state machine for onboarding
class OnboardingStep(Enum):
    NAME = "name"
    ROLE = "role"
    INDUSTRY = "industry"
    COMPANY_SIZE = "company_size"
    WEBSITE_STATUS = "website_status"
    WEBSITE_URL = "website_url"
    GOALS = "goals"
    BUDGET = "budget"
    COMPLETE = "complete"

class SimpleOnboarding:
    def __init__(self):
        self.steps = [
            OnboardingStep.NAME,
            OnboardingStep.ROLE,
            OnboardingStep.INDUSTRY,
            OnboardingStep.COMPANY_SIZE,
            OnboardingStep.WEBSITE_STATUS,
            OnboardingStep.WEBSITE_URL,
            OnboardingStep.GOALS,
            OnboardingStep.BUDGET
        ]
        self.step_messages = {
            OnboardingStep.NAME: "خلّينا نبدأ بالتعارف… وش اسمك الأول؟",
            OnboardingStep.ROLE: "وش دورك في العمل؟",
            OnboardingStep.INDUSTRY: "نشاط شركتكم إيش؟ (مثال: تجارة إلكترونية، مطاعم، تعليم، تقنية…)",
            OnboardingStep.COMPANY_SIZE: "كم حجم الشركة؟",
            OnboardingStep.WEBSITE_STATUS: "عندكم موقع إلكتروني؟",
            OnboardingStep.WEBSITE_URL: "أرسل رابط الموقع (https://…)",
            OnboardingStep.GOALS: "وش أهم أهدافك التسويقية؟ اكتبها مفصولة بفواصل (،). مثال: زيادة الوعي، تحسين التحويلات، ترتيب SEO…",
            OnboardingStep.BUDGET: "كم تقريباً ميزانيتكم الشهرية للتسويق؟"
        }
        self.step_options = {
            OnboardingStep.ROLE: ["مدير/ة تسويق", "مختص/ة تسويق", "مالك/ـة مشروع", "رائد/ة أعمال", "مدير/ة عام", "أخرى"],
            OnboardingStep.COMPANY_SIZE: ["👤 شخص واحد (فريلانسر)", "👥 2–10 موظفين", "🏢 11–50 موظف", "🏗 51+ موظف"],
            OnboardingStep.WEBSITE_STATUS: ["✅ نعم – شغّال", "🔧 نعم – يحتاج تطوير", "🏗 تحت الإنشاء", "❌ لا"],
            OnboardingStep.BUDGET: ["أقل من 5,000 ريال", "5,000–15,000 ريال", "15,000–50,000 ريال", "أكثر من 50,000 ريال", "حسب المشروع", "مو محددة"]
        }
        
        # Name validation
        self._AR = re.compile(r"^[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s\-']{2,40}$")
        self._LAT = re.compile(r"^[A-Za-z\s\-']{2,40}$")
        self._NON_NAMES = {
            "ايه", "أيه", "ايوه", "أيوه", "نعم", "لا", "تمام", "طيب", "اوكي", "أوكي", "اوكيه",
            "مرحبا", "اهلا", "أهلا", "هلا", "thanks", "thank you", "ok", "okay", "hello", "hi", "hey"
        }
        
        # URL validation
        self._URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
        
        # Store user sessions
        self.sessions = {}
    
    def _clean_name(self, s: str) -> Optional[str]:
        s = (s or "").strip()
        if not s:
            return None
        low = s.lower()
        if low in self._NON_NAMES:
            return None
        if self._AR.match(s) or self._LAT.match(s):
            return s if not s.isascii() else s.title()
        return None
    
    def _clean_url(self, s: str) -> Optional[str]:
        s = (s or "").strip()
        return s if s and self._URL_RE.match(s) else None
    
    def start_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Start onboarding for a new user"""
        self.sessions[user_id] = {
            "current_step": 0,
            "data": {},
            "step": OnboardingStep.NAME
        }
        return self._get_current_ui(user_id)
    
    def resume_onboarding(self, user_id: str, value: str) -> Dict[str, Any]:
        """Resume onboarding with user input"""
        if user_id not in self.sessions:
            return self.start_onboarding(user_id)
        
        session = self.sessions[user_id]
        current_step = session["step"]
        
        # Validate and save input
        if current_step == OnboardingStep.NAME:
            name = self._clean_name(value)
            if not name:
                return {
                    "done": False,
                    "ui": {
                        "ui_type": "input",
                        "message": "اسم غير واضح. اكتب اسمك الأول فقط (مثال: سارة، محمد، Laila). تجنب كلمات مثل: ايه، نعم، اوكي.",
                        "state_updates": {"node": "intro_name", "step": 1, "total": 8}
                    }
                }
            session["data"]["user_name"] = name
            
        elif current_step == OnboardingStep.ROLE:
            session["data"]["user_role"] = value
            
        elif current_step == OnboardingStep.INDUSTRY:
            session["data"]["industry"] = value.strip()
            
        elif current_step == OnboardingStep.COMPANY_SIZE:
            session["data"]["company_size"] = value
            
        elif current_step == OnboardingStep.WEBSITE_STATUS:
            session["data"]["website_status"] = "Yes" if value.startswith("✅") or value.startswith("🔧") else "No"
            # Skip website URL step if user doesn't have a website
            if session["data"]["website_status"] == "No":
                session["current_step"] += 2  # Skip the website URL step (go directly to goals)
                if session["current_step"] >= len(self.steps):
                    # Onboarding complete
                    session["step"] = OnboardingStep.COMPLETE
                    return {
                        "done": True,
                        "ui": None,
                        "profile": session["data"]
                    }
                # Get next step (skip website_url)
                session["step"] = self.steps[session["current_step"]]
                return self._get_current_ui(user_id)
            
        elif current_step == OnboardingStep.WEBSITE_URL:
            url = self._clean_url(value)
            if not url:
                return {
                    "done": False,
                    "ui": {
                        "ui_type": "input",
                        "message": "الرابط غير صالح. مثال: https://example.com",
                        "state_updates": {"node": "website_url", "step": 6, "total": 8}
                    }
                }
            session["data"]["website_url"] = url
            
        elif current_step == OnboardingStep.GOALS:
            items = [x.strip() for x in re.split(r"[،,]", value) if x.strip()]
            session["data"]["primary_goals"] = items or []
            
        elif current_step == OnboardingStep.BUDGET:
            session["data"]["budget_range"] = value
        
        # Move to next step
        session["current_step"] += 1
        
        if session["current_step"] >= len(self.steps):
            # Onboarding complete
            session["step"] = OnboardingStep.COMPLETE
            return {
                "done": True,
                "ui": None,
                "profile": session["data"]
            }
        
        # Get next step
        session["step"] = self.steps[session["current_step"]]
        return self._get_current_ui(user_id)
    
    def _get_current_ui(self, user_id: str) -> Dict[str, Any]:
        """Get the UI for the current step"""
        session = self.sessions[user_id]
        step = session["step"]
        
        # Calculate actual step number (accounting for conditional steps)
        step_num = session["current_step"] + 1
        total_steps = 8  # Total possible steps
        
        message = self.step_messages[step]
        options = self.step_options.get(step)
        
        ui_type = "options" if options else "input"
        
        return {
            "done": False,
            "ui": {
                "ui_type": ui_type,
                "message": message,
                "options": options,
                "state_updates": {"node": step.value, "step": step_num, "total": total_steps}
            }
        }

def _to_uuid_str(user_id: str) -> str:
    """Return a valid UUID string for any incoming user_id."""
    try:
        return str(uuid.UUID(str(user_id)))
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"onb:{user_id}"))

def _save_profile_to_db(user_id: str, profile_data: Dict[str, Any]) -> None:
    """Save profile data to Supabase"""
    if not _sb:
        print(f"[onboarding] Supabase not available, skipping save")
        return
    
    try:
        # Prepare payload with only allowed keys
        payload = {k: v for k, v in profile_data.items() if k in _ALLOWED_DB_KEYS}
        payload["user_id"] = _to_uuid_str(user_id)
        
        # Save to database
        _sb.table("profiles").upsert(payload, on_conflict="user_id").execute()
        print(f"[onboarding] saved profile for {user_id} -> {payload.get('user_id')}")
        print(f"[onboarding] profile data: {payload}")
    except Exception as e:
        print(f"[onboarding] failed to save profile: {e}")

# Global instance
onboarding = SimpleOnboarding()

def start_onboarding(user_id: str) -> Dict[str, Any]:
    """API function to start onboarding"""
    print(f"[onboarding] starting for user_id: {user_id}")
    result = onboarding.start_onboarding(user_id)
    return {
        "conversation_id": f"onb:{user_id}",
        "done": result["done"],
        "ui": result["ui"]
    }

def resume_onboarding(user_id: str, value: Any) -> Dict[str, Any]:
    """API function to resume onboarding"""
    print(f"[onboarding] resuming for user_id: {user_id} with value: {value}")
    result = onboarding.resume_onboarding(user_id, str(value))
    if result["done"]:
        print(f"[onboarding] completed for user_id: {user_id}")
        # Save profile to database
        _save_profile_to_db(user_id, result.get("profile", {}))
        return {
            "conversation_id": f"onb:{user_id}",
            "done": True,
            "ui": {
                "ui_type": "input",
                "message": f"تم يا {result.get('profile', {}).get('user_name', 'ضيفنا الكريم')}! ✅ الآن اسألني أي شيء في التسويق وبعطيك توصيات عملية.",
                "state_updates": {"node": "complete", "step": 8, "total": 8}
            },
            "profile": result.get("profile", {})
        }
    return {
        "conversation_id": f"onb:{user_id}",
        "done": False,
        "ui": result["ui"]
    }
