import requests
import os
from tools.supabase_client import supabase
from .formatters import format_social_post

def _check_posts_table_structure():
    """Internal function to check Supabase connection and posts table structure."""
    try:
        response = supabase.table("posts").select("*").limit(1).execute()
        
        if response.data:
            post = response.data[0]
            return {
                "success": True,
                "data": post,
                "columns": list(post.keys())
            }
        else:
            return {
                "success": False,
                "error": "No posts found in database"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Supabase Error: {str(e)}"
        }

def fetch_posts_summary() -> str:
    """Fetches and formats latest social media posts."""
    try:
        # First, check table structure
        table_check = _check_posts_table_structure()
        if not table_check["success"]:
            return f"⚠️ خطأ في الاتصال: {table_check['error']}"

        # If check successful, try actual fetch
        available_columns = table_check.get("columns", [])
        
        # Determine which order column to use
        order_column = (
            "published_date" if "published_date" in available_columns
            else "created_at" if "created_at" in available_columns
            else "reach"  # fallback to reach if no date columns
        )

        result = supabase.table("posts") \
            .select(",".join(available_columns)) \
            .order(order_column, desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "📭 لم يتم العثور على أي منشورات حديثة."

        # Format each post
        formatted_posts = []
        for post in result.data:
            try:
                formatted = format_social_post(post)
                formatted_posts.append(formatted)
            except Exception as e:
                formatted_posts.append("⚠️ خطأ في معالجة هذا المنشور")

        # Combine all posts with header
        return "📱 آخر تحليل للمنشورات على وسائل التواصل:\n\n" + \
               "\n\n".join(formatted_posts)

    except Exception as e:
        return f"❌ فشل في جلب المنشورات: {str(e)}"