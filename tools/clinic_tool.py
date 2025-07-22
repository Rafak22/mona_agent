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
    Answers user questions about Bassim Clinic from local structured data.
    Responds in the same language as the input and only answers the specific topic.
    """
    q = question.lower()
    is_ar = is_arabic(q)

    def ar(reply):
        return f"{reply}\n\n🧠 (تم جمع هذه البيانات الذكية عبر مونا — وكيلتك الذكية اللي تتعامل مع كل التفاصيل بدقة 💼)"

    def en(reply):
        return f"{reply}\n\n🧠 (Insight provided by Mona — your intelligent agent who handles every detail with precision 💼)"

    if "location" in q or "وين" in q or "الموقع" in q:
        return ar(f"📍 موقع العيادة: {clinic_data['location']}") if is_ar else en(f"📍 Clinic location: {clinic_data['location']}")

    elif "services" in q or "وش تقدم" in q or "الخدمات" in q or "تخصصات" in q:
        services = ", ".join(clinic_data["services"])
        return ar(f"💼 خدمات العيادة تشمل: {services}") if is_ar else en(f"💼 Clinic services include: {services}")

    elif "audience" in q or "جمهور" in q or "الفئة المستهدفة" in q or "فئة" in q:
        segments = ", ".join(clinic_data["audience_segments"])
        return ar(f"👥 الفئة المستهدفة: {segments}") if is_ar else en(f"👥 Target audience: {segments}")

    elif "goal" in q or "هدف" in q or "الأهداف" in q:
        goals = ", ".join(clinic_data["goals"])
        return ar(f"🎯 الأهداف التسويقية: {goals}") if is_ar else en(f"🎯 Marketing goals: {goals}")

    elif "حجم السوق" in q or "industry" in q or "market" in q:
        size = clinic_data["industry_insights"]["clinic_market_size_saudi"]
        return ar(f"📊 حجم سوق العيادات في السعودية: {size}") if is_ar else en(f"📊 Clinic market size in Saudi Arabia: {size}")

    elif "إعلانات" in q or "الحالية" in q or "current" in q or "جهود" in q:
        current = clinic_data["current_marketing"]
        if is_ar:
            return ar(
                f"📣 الجهود التسويقية الحالية:\n"
                f"- القنوات: {', '.join(current['channels'])}\n"
                f"- نقاط القوة: {', '.join(current['strengths'])}\n"
                f"- التحديات: {', '.join(current['challenges'])}"
            )
        else:
            return en(
                f"📣 Current marketing efforts:\n"
                f"- Channels: {', '.join(current['channels'])}\n"
                f"- Strengths: {', '.join(current['strengths'])}\n"
                f"- Challenges: {', '.join(current['challenges'])}"
            )

    elif "challenge" in q or "تحديات" in q:
        return ar(f"⚠️ التحديات: {', '.join(clinic_data['current_marketing']['challenges'])}") if is_ar else en(f"⚠️ Challenges: {', '.join(clinic_data['current_marketing']['challenges'])}")

    elif "الحجم" in q or "size" in q:
        return ar(f"🏢 حجم العيادة: {clinic_data['clinic_size']}") if is_ar else en(f"🏢 Clinic size: {clinic_data['clinic_size']}")

    else:
        return "❓ أحتاج توضيح أكثر لسؤالك عن العيادة. ممكن تعيد صياغته؟" if is_ar else "❓ I need more clarity to answer your clinic question. Could you rephrase it?"
