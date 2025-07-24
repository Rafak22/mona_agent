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
        services = ", ".join(clinic_data["services"][lang])
        return wrap_response(f"💼 {'خدمات العيادة تشمل' if is_ar else 'Clinic services include'}: {services}")

    elif "جمهور" in q or "الفئة المستهدفة" in q or "audience" in q:
        audience = ", ".join(clinic_data["audience_segments"][lang])
        return wrap_response(f"👥 {'الفئة المستهدفة' if is_ar else 'Target audience'}: {audience}")

    elif "goal" in q or "الأهداف" in q or "هدف" in q:
        goals = ", ".join(clinic_data["goals"][lang])
        return wrap_response(f"🎯 {'الأهداف التسويقية' if is_ar else 'Marketing goals'}: {goals}")

    elif "حجم السوق" in q or "industry" in q or "market" in q:
        size = clinic_data["industry_insights"]["clinic_market_size_saudi"][lang]
        return wrap_response(f"📊 {'حجم سوق العيادات في السعودية' if is_ar else 'Clinic market size in Saudi Arabia'}: {size}")

    elif "إعلانات" in q or "جهود" in q or "current" in q or "الحالية" in q:
        m = clinic_data["current_marketing"]
        channels = ", ".join(m["channels"][lang])
        strengths = ", ".join(m["strengths"][lang])
        challenges = ", ".join(m["challenges"][lang])
        return wrap_response(
            f"📣 {'الجهود التسويقية الحالية' if is_ar else 'Current marketing efforts'}:\n"
            f"- {'القنوات' if is_ar else 'Channels'}: {channels}\n"
            f"- {'نقاط القوة' if is_ar else 'Strengths'}: {strengths}\n"
            f"- {'التحديات' if is_ar else 'Challenges'}: {challenges}"
        )

    elif "challenge" in q or "تحديات" in q:
        challenges = ", ".join(clinic_data["current_marketing"]["challenges"][lang])
        return wrap_response(f"⚠️ {'التحديات' if is_ar else 'Challenges'}: {challenges}")

    elif "الحجم" in q or "size" in q:
        size = clinic_data["clinic_size"][lang]
        return wrap_response(f"🏢 {'حجم العيادة' if is_ar else 'Clinic size'}: {size}")

    elif "رؤية" in q or "vision" in q:
        vision = clinic_data["vision"][lang]
        return wrap_response(f"🔭 {'رؤية العيادة' if is_ar else 'Clinic vision'}: {vision}")

    elif "social" in q or "انستغرام" in q or "تيك توك" in q or "روابط" in q:
        sm = clinic_data["social_media"]
        return wrap_response(
            f"🌐 {'روابط التواصل الاجتماعي' if is_ar else 'Social media links'}:\n"
            f"- Instagram: {sm['instagram']}\n"
            f"- TikTok: {sm['tiktok']}"
        )

    elif "تعريف" in q or "ما هي" in q or "من أنتم" in q or "description" in q:
        return wrap_response(f"ℹ️ {clinic_data['description'][lang]}")

    else:
        return "❓ أحتاج توضيح أكثر لسؤالك عن العيادة. ممكن تعيد صياغته؟" if is_ar else "❓ I need more clarity to answer you about the clinic. Can you rephrase it?"
