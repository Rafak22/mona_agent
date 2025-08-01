from datetime import datetime
from .supabase_client import supabase

def fetch_seo_signals_summary() -> str:
    """
    Fetches latest SEO metrics from the seo_signals table.
    Schema:
    - keyword: string
    - position: int
    - volume: int
    - cpc: float
    - competition: float
    """
    try:
        result = supabase.table("seo_signals") \
            .select("keyword,position,volume,cpc,competition") \
            .order("volume", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "لم يتم العثور على أي تحليلات SEO حديثة."

        signals = result.data
        summary_parts = ["🔍 آخر تحليل لتحسين محركات البحث:\n"]

        for signal in signals:
            competition_level = (
                "عالية 🔴" if signal["competition"] > 0.66 else
                "متوسطة 🟡" if signal["competition"] > 0.33 else
                "منخفضة 🟢"
            )
            
            summary_parts.append(
                f"• الكلمة المفتاحية: {signal['keyword']}\n"
                f"  - الموقع: {signal['position']} 📊\n"
                f"  - حجم البحث: {signal['volume']} 🔍\n"
                f"  - تكلفة النقرة: ${signal['cpc']:.2f} 💰\n"
                f"  - المنافسة: {competition_level}\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching SEO signals: {e}")
        return "عذراً، حدث خطأ أثناء جلب بيانات تحسين محركات البحث."