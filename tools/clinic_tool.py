import json
import os
import re
from langchain.tools import tool

CLINIC_DATA_PATH = os.path.join(os.path.dirname(__file__), "../clinic_data.json")

def load_clinic_data():
    with open(CLINIC_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

clinic_data = load_clinic_data()

def is_arabic(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))

@tool
def fetch_clinic_info(question: str) -> str:
    """
    Answers user questions about Bassim Clinic from local bilingual JSON.
    Responds in Arabic if the question is in Arabic, otherwise responds in English.
    Only the specifically requested field is returned.
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

    if "location" in q or "وين" in q or "الموقع" in q:
        return wrap_response(f"📍 {clinic_data['location'][lang]}")

    elif "working hours" in q or "business hours" in q or "ساعات العمل" in q or "اوقات الدوام" in q:
        return wrap_response(f"🕘 {clinic_data['business_hours'][lang]}")

    elif "services" in q or "وش تقدم" in q or "الخدمات" in q or "تخصصات" in q:
        services_list = clinic_data.get("services", {}).get(lang)
        if services_list:
            services = "\n".join([f"• {item}" for item in services_list])
            return wrap_response(f"💼 {'خدمات العيادة تشمل' if is_ar else 'Clinic services include'}:\n{services}")
        else:
            return wrap_response("لم أتمكن من العثور على قائمة الخدمات حاليًا." if is_ar else "Service list not found.")

    elif "جمهور" in q or "الفئة المستهدفة" in q or "audience" in q:
        audience_list = clinic_data.get("audience_segments", {}).get(lang)
        if audience_list:
            audience = "\n".join([f"• {item}" for item in audience_list])
            return wrap_response(f"👥 {'الفئة المستهدفة' if is_ar else 'Target audience'}:\n{audience}")
        else:
            return wrap_response("لا توجد معلومات عن الفئة المستهدفة." if is_ar else "Target audience info not found.")

    elif "goal" in q or "الأهداف" in q or "هدف" in q:
        goals_list = clinic_data.get("goals", {}).get(lang)
        if goals_list:
            goals = "\n".join([f"• {item}" for item in goals_list])
            return wrap_response(f"🎯 {'الأهداف التسويقية' if is_ar else 'Marketing goals'}:\n{goals}")
        else:
            return wrap_response("لا توجد أهداف واضحة حالياً." if is_ar else "Marketing goals not found.")

    elif "حجم السوق" in q or "industry" in q or "market" in q:
        size = clinic_data.get("industry_insights", {}).get("clinic_market_size_saudi", {}).get(lang)
        return wrap_response(
            f"📊 {'حجم سوق العيادات في السعودية' if is_ar else 'Clinic market size in Saudi Arabia'}: {size}"
        ) if size else wrap_response("لا توجد بيانات عن حجم السوق." if is_ar else "Market size data not available.")

    elif (
        "إعلانات" in q or "جهود" in q or "current" in q or "الحالية" in q
        or "القنوات" in q or "التسويقية" in q or "قنوات التسويق" in q or "channels" in q
    ):
        m = clinic_data.get("current_marketing", {})
        channels = m.get("channels", {}).get(lang, [])
        strengths = m.get("strengths", {}).get(lang, [])
        challenges = m.get("challenges", {}).get(lang, [])
        return wrap_response(
            f"📣 {'الجهود التسويقية الحالية' if is_ar else 'Current marketing efforts'}:\n"
            f"- {'القنوات' if is_ar else 'Channels'}: {', '.join(channels)}\n"
            f"- {'نقاط القوة' if is_ar else 'Strengths'}: {', '.join(strengths)}\n"
            f"- {'التحديات' if is_ar else 'Challenges'}: {', '.join(challenges)}"
        )

    elif "challenge" in q or "تحديات" in q:
        challenges = clinic_data.get("current_marketing", {}).get("challenges", {}).get(lang, [])
        return wrap_response(
            f"⚠️ {'التحديات' if is_ar else 'Challenges'}:\n" + "\n".join([f"• {c}" for c in challenges])
        ) if challenges else wrap_response("لا توجد تحديات مسجلة حالياً." if is_ar else "No challenges listed.")

    elif "الحجم" in q or "size" in q:
        size = clinic_data.get("clinic_size", {}).get(lang)
        return wrap_response(f"🏢 {'حجم العيادة' if is_ar else 'Clinic size'}: {size}") if size else wrap_response("لا توجد بيانات عن حجم العيادة." if is_ar else "Clinic size data not found.")

    elif "رؤية" in q or "vision" in q:
        vision = clinic_data.get("vision", {}).get(lang)
        return wrap_response(f"🔭 {'رؤية العيادة' if is_ar else 'Clinic vision'}: {vision}") if vision else wrap_response("لا توجد رؤية واضحة حالياً." if is_ar else "Vision not available.")

    elif "social" in q or "انستغرام" in q or "تيك توك" in q or "روابط" in q:
        sm = clinic_data.get("social_media", {})
        insta = sm.get("instagram", "غير متوفر")
        tiktok = sm.get("tiktok", "غير متوفر")
        return wrap_response(
            f"🌐 {'روابط التواصل الاجتماعي' if is_ar else 'Social media links'}:\n"
            f"- Instagram: {insta}\n"
            f"- TikTok: {tiktok}"
        )

    elif "تعريف" in q or "ما هي" in q or "من أنتم" in q or "description" in q:
        description = clinic_data.get("description", {}).get(lang)
        return wrap_response(f"ℹ️ {description}") if description else wrap_response("لا يوجد وصف حالياً." if is_ar else "No description available.")

    else:
        return "❓ أحتاج توضيح أكثر لسؤالك عن العيادة. ممكن تعيد صياغته؟" if is_ar else "❓ I need more clarity to answer you about the clinic. Can you rephrase it?"
