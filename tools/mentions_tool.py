import requests
import os
from datetime import datetime
from tools.supabase_client import supabase

def _check_mentions_table_structure():
    """
    Internal function to check Supabase connection and mentions table structure.
    """
    try:
        response = supabase.table("mentions").select("*").limit(1).execute()
        
        if response.data:
            mention = response.data[0]
            return {
                "success": True,
                "data": mention,
                "columns": list(mention.keys())
            }
        else:
            return {
                "success": False,
                "error": "No mentions found in database"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Supabase Error: {str(e)}"
        }

def fetch_mentions_summary() -> str:
    """
    Fetches latest brand mentions with detailed error reporting.
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
        # First, check table structure
        table_check = _check_mentions_table_structure()
        if not table_check["success"]:
            return f"⚠️ خطأ في الاتصال: {table_check['error']}"

        # If check successful, try actual fetch with correct columns
        available_columns = table_check.get("columns", [])
        
        # Determine which order column to use
        order_column = (
            "published_date" if "published_date" in available_columns
            else "collected_date" if "collected_date" in available_columns
            else "created_at" if "created_at" in available_columns
            else "id"  # fallback to id if no date columns
        )

        result = supabase.table("mentions") \
            .select(",".join(available_columns)) \
            .order(order_column, desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "📭 لم يتم العثور على أي ذكر حديث للعلامة التجارية."

        mentions = result.data
        summary_parts = ["📊 آخر تحليل لذكر العلامة التجارية:\n"]

        for mention in mentions:
            try:
                # Try to get date from any available date column
                date_str = (
                    mention.get("published_date") or 
                    mention.get("collected_date") or 
                    mention.get("created_at", "N/A")
                )
                date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d") if date_str != "N/A" else "N/A"
                
                sentiment = {
                    "positive": "✨ إيجابي",
                    "negative": "⚠️ سلبي",
                    "neutral": "📝 محايد"
                }.get(mention.get("sentiment"), "❓ غير محدد")

                sentiment_score = mention.get("sentiment_score", 0)
                sentiment_emoji = "🟢" if sentiment_score > 0.3 else "🔴" if sentiment_score < -0.3 else "⚪"

                summary_parts.append(
                    f"• {date} | {sentiment} {sentiment_emoji}\n"
                    f"  - المنصة: {mention.get('platform', 'غير معروف')}\n"
                    f"  - الكاتب: {mention.get('author', 'مجهول')}\n"
                    f"  - المحتوى: {mention.get('mention_text', '[لا يوجد نص]')[:100]}...\n"
                    f"  - التفاعل: {mention.get('engagement', '0')} 👥\n"
                )
            except Exception as mention_e:
                print(f"🔥 Error processing mention: {mention_e}")
                print(f"Mention data: {mention}")
                summary_parts.append("⚠️ خطأ في معالجة هذا المنشور")

        return "\n".join(summary_parts)

    except Exception as e:
        error_msg = f"🔥 Error fetching mentions: {str(e)}"
        print(error_msg)
        return f"❌ فشل في جلب البيانات:\n{error_msg}"