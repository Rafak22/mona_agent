import re
from .supabase_client import supabase

def is_arabic(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))

def fetch_clinic_info_from_db(question: str) -> str:
    """
    Answers user questions about Bassim Clinic from Supabase database.
    Responds in Arabic if the question is in Arabic, otherwise responds in English.
    """
    q = question.lower()
    is_ar = is_arabic(q)
    lang = "ar" if is_ar else "en"

    def wrap_response(content):
        return (
            f"{content}\n\n🧠 (تم جمع هذه البيانات الذكية عبر مورفو — وكيلتك الذكية اللي تتعامل مع كل التفاصيل بدقة 💼)"
            if is_ar else
            f"{content}\n\n🧠 (Insight provided by MORVO — your intelligent agent who handles every detail with precision 💼)"
        )

    # Query mapping for different types of questions
    query_mapping = {
        "location": ["location", "وين", "الموقع"],
        "business_hours": ["working hours", "business hours", "ساعات العمل", "اوقات الدوام"],
        "services": ["services", "وش تقدم", "الخدمات", "تخصصات"],
        "audience_segments": ["جمهور", "الفئة المستهدفة", "audience"],
        "goals": ["goal", "الأهداف", "هدف"],
        "industry_insights": ["حجم السوق", "industry", "market"],
        "current_marketing": ["إعلانات", "جهود", "current", "الحالية", "القنوات", "التسويقية", "قنوات التسويق", "channels"],
        "challenges": ["challenge", "تحديات"],
        "clinic_size": ["الحجم", "size"],
        "vision": ["رؤية", "vision"],
        "social_media": ["social", "انستغرام", "تيك توك", "روابط"],
        "description": ["تعريف", "ما هي", "من أنتم", "description"]
    }

    # Find which field to query based on keywords
    field_to_query = None
    for field, keywords in query_mapping.items():
        if any(keyword in q for keyword in keywords):
            field_to_query = field
            break

    if not field_to_query:
        return "❓ لم أتمكن من العثور على معلومة دقيقة. ممكن توضح سؤالك أكثر؟" if is_ar else "❓ I need more clarity. Can you rephrase your question?"

    try:
        # Query Supabase for the specific field
        result = supabase.table("clinic_info").select(field_to_query).single().execute()
        
        if not result.data:
            return "❓ لم أتمكن من العثور على معلومة دقيقة. ممكن توضح سؤالك أكثر؟" if is_ar else "❓ I need more clarity. Can you rephrase your question?"

        data = result.data[field_to_query]

        # Handle different field types
        if field_to_query == "location":
            return wrap_response(f"📍 {data[lang]}")
        
        elif field_to_query == "business_hours":
            return wrap_response(f"🕘 {data[lang]}")
        
        elif field_to_query == "services":
            services = "\n".join([f"• {item}" for item in data[lang]])
            return wrap_response(f"💼 {'خدمات العيادة تشمل' if is_ar else 'Clinic services include'}:\n{services}")
        
        elif field_to_query == "audience_segments":
            audience = "\n".join([f"• {item}" for item in data[lang]])
            return wrap_response(f"👥 {'الفئة المستهدفة' if is_ar else 'Target audience'}:\n{audience}")
        
        elif field_to_query == "goals":
            goals = "\n".join([f"• {item}" for item in data[lang]])
            return wrap_response(f"🎯 {'الأهداف التسويقية' if is_ar else 'Marketing goals'}:\n{goals}")
        
        elif field_to_query == "industry_insights":
            size = data.get("clinic_market_size_saudi", {}).get(lang)
            return wrap_response(
                f"📊 {'حجم سوق العيادات في السعودية' if is_ar else 'Clinic market size in Saudi Arabia'}: {size}"
            )
        
        elif field_to_query == "current_marketing":
            channels = data.get("channels", {}).get(lang, [])
            strengths = data.get("strengths", {}).get(lang, [])
            challenges = data.get("challenges", {}).get(lang, [])
            return wrap_response(
                f"📣 {'الجهود التسويقية الحالية' if is_ar else 'Current marketing efforts'}:\n"
                f"- {'القنوات' if is_ar else 'Channels'}: {', '.join(channels)}\n"
                f"- {'نقاط القوة' if is_ar else 'Strengths'}: {', '.join(strengths)}\n"
                f"- {'التحديات' if is_ar else 'Challenges'}: {', '.join(challenges)}"
            )
        
        elif field_to_query == "challenges":
            challenges = data.get("challenges", {}).get(lang, [])
            return wrap_response(
                f"⚠️ {'التحديات' if is_ar else 'Challenges'}:\n" + "\n".join([f"• {c}" for c in challenges])
            )
        
        elif field_to_query == "clinic_size":
            return wrap_response(f"🏢 {'حجم العيادة' if is_ar else 'Clinic size'}: {data[lang]}")
        
        elif field_to_query == "vision":
            return wrap_response(f"🔭 {'رؤية العيادة' if is_ar else 'Clinic vision'}: {data[lang]}")
        
        elif field_to_query == "social_media":
            insta = data.get("instagram", "غير متوفر")
            tiktok = data.get("tiktok", "غير متوفر")
            return wrap_response(
                f"🌐 {'روابط التواصل الاجتماعي' if is_ar else 'Social media links'}:\n"
                f"- Instagram: {insta}\n"
                f"- TikTok: {tiktok}"
            )
        
        elif field_to_query == "description":
            return wrap_response(f"ℹ️ {data[lang]}")

    except Exception as e:
        print(f"Error querying Supabase: {e}")
        return "❓ لم أتمكن من العثور على معلومة دقيقة. ممكن توضح سؤالك أكثر؟" if is_ar else "❓ I need more clarity. Can you rephrase your question?"