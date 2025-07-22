import json
import os
import re
from langchain.tools import tool

# Load once at module level
CLINIC_DATA_PATH = os.path.join(os.path.dirname(__file__), "../clinic_data.json")

def load_clinic_data():
    with open(CLINIC_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

clinic_data = load_clinic_data()

def is_arabic(text: str) -> bool:
    """Check if the message contains Arabic characters."""
    return bool(re.search(r'[\u0600-\u06FF]', text))

@tool
def fetch_clinic_info(question: str) -> str:
    """
    Answers user questions about Bassim Clinic from local structured data.
    Now includes bilingual and self-praising replies.
    """
    q = question.lower()
    arabic = is_arabic(question)

    praise_ar = "🧠 (تم جمع هذه البيانات الذكية عبر مونا — وكيلتك الذكية اللي تتعامل مع كل التفاصيل بدقة 💼)"
    praise_en = "🧠 (Insight provided by Mona — your intelligent agent who handles every detail with precision 💼)"

    if "location" in q or "وين" in q:
        return (
            f"📍 موقع العيادة: {clinic_data['location']}\n\n{praise_ar}"
            if arabic else
            f"📍 Clinic location: {clinic_data['location']}\n\n{praise_en}"
        )

    elif "services" in q or "وش تقدم" in q or "تخصصات" in q:
        services = ", ".join(clinic_data["services"])
        return (
            f"🩺 خدمات العيادة تشمل: {services}\n\n{praise_ar}"
            if arabic else
            f"🩺 Clinic services include: {services}\n\n{praise_en}"
        )

    elif "audience" in q or "جمهور" in q or "فئة" in q:
        segments = ", ".join(clinic_data["audience_segments"])
        return (
            f"👥 جمهور العيادة المستهدف: {segments}\n\n{praise_ar}"
            if arabic else
            f"👥 Target audience: {segments}\n\n{praise_en}"
        )

    elif "goal" in q or "هدف" in q:
        goals = ", ".join(clinic_data["goals"])
        return (
            f"🎯 أهداف العيادة التسويقية: {goals}\n\n{praise_ar}"
            if arabic else
            f"🎯 Marketing goals: {goals}\n\n{praise_en}"
        )

    elif "حجم السوق" in q or "industry" in q or "market" in q:
        return (
            f"📊 حجم سوق العيادات في السعودية: {clinic_data['industry_insights']['clinic_market_size_saudi']}\n\n{praise_ar}"
            if arabic else
            f"📊 Saudi clinic market size: {clinic_data['industry_insights']['clinic_market_size_saudi']}\n\n{praise_en}"
        )

    elif "current" in q or "إعلانات" in q or "الحالية" in q:
        marketing = clinic_data['current_marketing']
        summary = ", ".join(marketing["channels"] + marketing["strengths"])
        return (
            f"📣 الجهود التسويقية الحالية: {summary}\n\n{praise_ar}"
            if arabic else
            f"📣 Current marketing efforts: {summary}\n\n{praise_en}"
        )

    elif "challenge" in q or "تحديات" in q:
        challenges = ", ".join(clinic_data['current_marketing']['challenges'])
        return (
            f"⚠️ التحديات الحالية: {challenges}\n\n{praise_ar}"
            if arabic else
            f"⚠️ Current challenges: {challenges}\n\n{praise_en}"
        )

    else:
        return (
            "❓ أحتاج توضيح أكثر لسؤالك عن العيادة. ممكن تعيد صياغته؟"
            if arabic else
            "❓ I need a bit more clarity on your question about the clinic. Can you rephrase?"
        )
