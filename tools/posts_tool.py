from .supabase_client import supabase
from .formatters import format_social_post

def debug_fetch_latest_post():
    """Debug function to check Supabase connection and posts table structure."""
    try:
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
    """Fetches and formats latest social media posts."""
    try:
        # First, run debug check
        debug_result = debug_fetch_latest_post()
        if not debug_result["success"]:
            return f"⚠️ خطأ في الاتصال: {debug_result['error']}"

        # If debug successful, try actual fetch
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

        # Format each post
        formatted_posts = []
        for post in result.data:
            try:
                formatted = format_social_post(post)
                formatted_posts.append(formatted)
            except Exception as e:
                print(f"Error formatting post: {e}")
                print(f"Post data: {post}")
                formatted_posts.append("⚠️ خطأ في معالجة هذا المنشور")

        # Combine all posts with header
        return "📱 آخر تحليل للمنشورات على وسائل التواصل:\n\n" + \
               "\n\n".join(formatted_posts)

    except Exception as e:
        error_msg = f"🔥 Error fetching posts: {str(e)}"
        print(error_msg)
        return f"❌ فشل في جلب المنشورات:\n{error_msg}"