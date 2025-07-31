from datetime import datetime
from .supabase_client import supabase

def fetch_mentions_summary(limit: int = 5) -> str:
    """
    Fetches the latest brand mentions from Supabase and formats them for display.
    """
    try:
        result = (
            supabase.table("mentions")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        if not result.data:
            return "🔍 لم يتم العثور على أي ذكر للعلامة التجارية في الفترة الأخيرة."

        mentions = result.data
        summary_parts = ["📊 **آخر تحليل لذكر علامتك التجارية (Brand24):**\n"]

        sentiment_map = {
            "positive": "✨ إيجابي",
            "negative": "⚠️ سلبي",
            "neutral": "📝 محايد"
        }

        for mention in mentions:
            created_at = mention.get("created_at", "")
            source = mention.get("source", "غير معروف")
            content = mention.get("content", "لا يوجد محتوى")
            engagement = mention.get("engagement", "؟")
            sentiment = sentiment_map.get(mention.get("sentiment", "neutral"), "📝 محايد")

            try:
                date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d")
            except:
                date = "تاريخ غير معروف"

            summary_parts.append(
                f"• **{date}** | {sentiment}\n"
                f"  - 📰 المصدر: {source}\n"
                f"  - ✍️ المحتوى: {content[:100]}{'...' if len(content) > 100 else ''}\n"
                f"  - 👥 التفاعل: {engagement}\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching mentions: {e}")
        return "⚠️ عذراً، حدث خطأ أثناء جلب بيانات ذكر العلامة التجارية."
