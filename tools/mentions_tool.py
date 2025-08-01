from datetime import datetime
from .supabase_client import supabase

def fetch_mentions_summary() -> str:
    """
    Fetches latest brand mentions and sentiment from Supabase.
    """
    try:
        result = supabase.table("mentions") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "لم يتم العثور على أي ذكر حديث للعلامة التجارية."

        mentions = result.data
        summary_parts = ["📊 آخر تحليل لذكر العلامة التجارية:\n"]

        for mention in mentions:
            date = datetime.fromisoformat(mention["created_at"]).strftime("%Y-%m-%d")
            sentiment = {
                "positive": "✨ إيجابي",
                "negative": "⚠️ سلبي",
                "neutral": "📝 محايد"
            }.get(mention["sentiment"], "📝 محايد")

            summary_parts.append(
                f"• {date} | {sentiment}\n"
                f"  - المصدر: {mention['source']}\n"
                f"  - المحتوى: {mention['content'][:100]}...\n"
                f"  - التفاعل: {mention['engagement']} 👥\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching mentions: {e}")
        return "عذراً، حدث خطأ أثناء جلب بيانات ذكر العلامة التجارية."