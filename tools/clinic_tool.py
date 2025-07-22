import json
import os
from langchain.tools import tool

# Load once at module level
CLINIC_DATA_PATH = os.path.join(os.path.dirname(__file__), "../clinic_data.json")

def load_clinic_data():
    with open(CLINIC_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

clinic_data = load_clinic_data()

@tool
def fetch_clinic_info(question: str) -> str:
    """
    Answers user questions about Bassim Clinic from local structured data.
    """
    q = question.lower()

    if "location" in q or "وين" in q:
        return f"📍 موقع العيادة: {clinic_data['location']}"

    elif "services" in q or "وش تقدم" in q or "تخصصات" in q:
        services = ", ".join(clinic_data["services"])
        return f"🩺 خدمات العيادة تشمل: {services}"

    elif "audience" in q or "جمهور" in q or "فئة" in q:
        return f"👥 جمهور العيادة المستهدف: {clinic_data['audience_segments']}"

    elif "goal" in q or "هدف" in q:
        return f"🎯 أهداف العيادة التسويقية: {clinic_data['goals']}"

    elif "حجم السوق" in q or "industry" in q or "market" in q:
        return f"📊 حجم سوق العيادات في السعودية: {clinic_data['industry_insights']['clinic_market_size_saudi']}"

    elif "current" in q or "إعلانات" in q or "الحالية" in q:
        return f"📣 الجهود التسويقية الحالية: {clinic_data['current_marketing']}"

    elif "challenge" in q or "تحديات" in q:
        return f"⚠️ التحديات الحالية: {clinic_data['current_marketing']['challenges']}"

    else:
        return "❓ أحتاج توضيح أكثر لسؤالك عن العيادة. ممكن تعيد صياغته؟" 