from datetime import datetime
from .supabase_client import supabase

def fetch_mentions_summary() -> str:
    """
    Fetches latest brand mentions from the mentions table.
    Schema:
    - mention_text: string
    - sentiment: string (positive, neutral, negative)
    - sentiment_score: float (-1.0 to 1.0)
    - platform: string
    - author: string
    - engagement: int
    - published_date: date
    """
    try:
        result = supabase.table("mentions") \
            .select("mention_text,sentiment,sentiment_score,platform,author,engagement,published_date") \
            .order("published_date", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "لم يتم العثور على أي ذكر حديث للعلامة التجارية."

        mentions = result.data
        summary_parts = ["📊 آخر تحليل لذكر العلامة التجارية:\n"]

        for mention in mentions:
            date = datetime.fromisoformat(mention["published_date"]).strftime("%Y-%m-%d")
            sentiment = {
                "positive": "✨ إيجابي",
                "negative": "⚠️ سلبي",
                "neutral": "📝 محايد"
            }.get(mention["sentiment"], "📝 محايد")
            
            score = mention["sentiment_score"]
            sentiment_emoji = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"

            summary_parts.append(
                f"• {date} | {sentiment} {sentiment_emoji}\n"
                f"  - المنصة: {mention['platform']}\n"
                f"  - الكاتب: {mention['author']}\n"
                f"  - المحتوى: {mention['mention_text'][:100]}...\n"
                f"  - التفاعل: {mention['engagement']} 👥\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching mentions: {e}")
        return "عذراً، حدث خطأ أثناء جلب بيانات ذكر العلامة التجارية."