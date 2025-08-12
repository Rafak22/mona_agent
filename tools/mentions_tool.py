import requests
import os
from datetime import datetime
from tools.supabase_client import supabase

def debug_fetch_latest_mention():
    """
    Debug function to check Supabase connection and mentions table structure.
    """
    try:
        response = supabase.table("mentions").select("*").limit(1).execute()
        
        print("🔍 DEBUG: Supabase Response")
        print(f"Status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
        
        if response.data:
            mention = response.data[0]
            print("✅ Found mention data:")
            print(f"Available columns: {list(mention.keys())}")
            return {
                "success": True,
                "data": mention,
                "columns": list(mention.keys())
            }
        else:
            print("⚠️ No mentions found in database")
            return {
                "success": False,
                "error": "No mentions found in database"
            }
    except Exception as e:
        error_msg = f"🔥 Supabase Error: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
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
        # First, run debug check
        debug_result = debug_fetch_latest_mention()
        if not debug_result["success"]:
            return f"⚠️ خطأ في الاتصال: {debug_result['error']}"

        # If debug successful, try actual fetch with correct columns
        available_columns = debug_result.get("columns", [])
        
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