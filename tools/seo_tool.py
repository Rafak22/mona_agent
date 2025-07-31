from datetime import datetime
from .supabase_client import supabase

def fetch_seo_signals_summary() -> str:
    """
    Fetches the latest 5 SEO signals from Supabase and formats them for display.
    """
    try:
        result = supabase.table("seo_signals") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "📈 لم يتم العثور على أي تحليلات SEO حديثة."

        signals = result.data
        summary_parts = ["🔍 آخر تحليل لتحسين محركات البحث (SE Ranking):\n"]

        for signal in signals:
            date = datetime.fromisoformat(signal["created_at"]).strftime("%Y-%m-%d")
            change = signal["position_change"]
            change_icon = "⬆️" if change > 0 else "⬇️" if change < 0 else "➡️"
            
            summary_parts.append(
                f"• {date} | الكلمة المفتاحية: {signal['keyword']}\n"
                f"  - الموقع: {signal['position']} {change_icon}\n"
                f"  - حجم البحث: {signal['search_volume']} 🔍\n"
                f"  - الصعوبة: {signal['difficulty']}/100 📊\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching SEO signals: {e}")
        return "⚠️ عذراً، حدث خطأ أثناء جلب بيانات تحسين محركات البحث."