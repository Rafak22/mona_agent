from datetime import datetime
from .supabase_client import supabase

def debug_fetch_latest_post():
    """
    Debug function to check Supabase connection and posts table structure.
    """
    try:
        # Try to fetch a single post without any ordering
        response = supabase.table("posts").select("*").limit(1).execute()
        
        print("🔍 DEBUG: Supabase Response")
        print(f"Status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
        
        if response.data:
            post = response.data[0]
            print("✅ Found post data:")
            print(f"Available columns: {list(post.keys())}")
            return {
                "success": True,
                "data": post,
                "columns": list(post.keys())
            }
        else:
            print("⚠️ No posts found in database")
            return {
                "success": False,
                "error": "No posts found in database"
            }
    except Exception as e:
        error_msg = f"🔥 Supabase Error: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def fetch_posts_summary() -> str:
    """
    Fetches latest social media posts from the posts table.
    Schema:
    - content: string
    - platform: string
    - hashtags: array/string
    - reach: int
    - ctr: float
    - published_date: date
    """
    try:
        # First, run debug check
        debug_result = debug_fetch_latest_post()
        if not debug_result["success"]:
            return f"⚠️ خطأ في الاتصال: {debug_result['error']}"

        # If debug successful, try actual fetch with correct columns
        available_columns = debug_result.get("columns", [])
        
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

        posts = result.data
        summary_parts = ["📱 آخر تحليل للمنشورات على وسائل التواصل:\n"]

        platform_icons = {
            "instagram": "📸",
            "tiktok": "🎵",
            "twitter": "🐦",
            "facebook": "👥",
            "linkedin": "💼"
        }

        for post in posts:
            try:
                # Try to get date from either column
                date_str = post.get("published_date") or post.get("created_at", "N/A")
                date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d") if date_str != "N/A" else "N/A"
                
                platform = post.get("platform", "unknown").lower()
                platform_icon = platform_icons.get(platform, "🌐")
                
                summary_parts.append(
                    f"• {date} | {platform_icon} {platform}\n"
                    f"  - المحتوى: {post.get('content', '[لا يوجد محتوى]')[:100]}...\n"
                    f"  - الوصول: {post.get('reach', '0')} 👀\n"
                    f"  - نسبة النقر: {post.get('ctr', '0')}% 🎯\n"
                )
            except Exception as post_e:
                print(f"🔥 Error processing post: {post_e}")
                print(f"Post data: {post}")
                summary_parts.append("⚠️ خطأ في معالجة هذا المنشور")

        return "\n".join(summary_parts)

    except Exception as e:
        error_msg = f"🔥 Error fetching posts: {str(e)}"
        print(error_msg)
        return f"❌ فشل في جلب المنشورات:\n{error_msg}"