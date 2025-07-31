from datetime import datetime
from .supabase_client import supabase

def fetch_seo_signals_summary(limit: int = 5) -> str:
    """
    Fetches the latest SEO signals from Supabase and formats them for display.
    """
    try:
        result = (
            supabase.table("seo_signals")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        if not result.data:
            return "📈 لم يتم العثور على أي تحليلات SEO حديثة."

        signals = result.data
        summary_parts = ["🔍 **آخر تحليل لتحسين محركات البحث (SE Ranking):**\n"]

        for signal in signals:
            created_at = signal.get("created_at", "")
            keyword = signal.get("keyword", "غير معروف")
            position = signal.get("position", "؟")
            volume = signal.get("search_volume", "؟")
            difficulty = signal.get("difficulty", "؟")
            change = signal.get("position_change", 0)

            try:
                date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d")
            except:
                date = "تاريخ غير معروف"

            change_icon = "⬆️" if change > 0 else "⬇️" if change < 0 else "➡️"

            summary_parts.append(
                f"• **{date}** | 🔑 الكلمة المفتاحية: {keyword}\n"
                f"  - 📍 الموقع: {position} {change_icon} (تغير: {change})\n"
                f"  - 🔍 حجم البحث: {volume}\n"
                f"  - 📊 الصعوبة: {difficulty}/100\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching SEO signals: {e}")
        return "⚠️ عذراً، حدث خطأ أثناء جلب بيانات تحسين محركات البحث."
