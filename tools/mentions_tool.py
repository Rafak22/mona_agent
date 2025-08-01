from datetime import datetime
from .supabase_client import supabase

def fetch_mentions_summary() -> str:
    """
    Fetches latest brand mentions with detailed error reporting.
    """
    try:
        response = supabase.table("mentions") \
            .select("mention_text,sentiment,sentiment_score,platform,author,engagement,published_date") \
            .order("published_date", desc=True) \
            .limit(5) \
            .execute()

        if not response.data:
            return "📭 لا توجد بيانات متاحة حالياً من Supabase."

        summaries = []
        for item in response.data:
            try:
                date = datetime.fromisoformat(item.get("published_date", "")).strftime("%Y-%m-%d")
                sentiment = {
                    "positive": "✨ إيجابي",
                    "negative": "⚠️ سلبي",
                    "neutral": "📝 محايد"
                }.get(item.get("sentiment"), "❓ غير محدد")

                summaries.append(
                    f"• {date} | {sentiment}\n"
                    f"👤 {item.get('author', 'مجهول')} على {item.get('platform', 'غير معروف')}:\n"
                    f"💬 {item.get('mention_text', '[لا يوجد نص]')[:100]}...\n"
                    f"📊 التفاعل: {item.get('engagement', '0')} 👥"
                )
            except KeyError as ke:
                print(f"🔍 Missing field in mention data: {ke}")
                print(f"🔍 Available fields: {item.keys()}")
                summaries.append("⚠️ بيانات غير مكتملة لهذا المنشور")
            except Exception as item_e:
                print(f"🔥 Error processing mention: {item_e}")
                summaries.append("❌ خطأ في معالجة هذا المنشور")

        return "\n\n".join(summaries) if summaries else "📭 لم نتمكن من معالجة أي بيانات."

    except Exception as e:
        error_msg = f"🔥 Supabase fetch error: {str(e)}"
        print(error_msg)
        return f"❌ فشل في الاتصال بـ Supabase:\n{error_msg}"