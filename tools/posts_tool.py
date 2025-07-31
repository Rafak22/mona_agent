from datetime import datetime
from .supabase_client import supabase

def fetch_posts_summary(limit: int = 5) -> str:
    """
    Fetches the latest social media posts from Supabase and formats them for display.
    """
    try:
        result = supabase.table("posts") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        if not result.data:
            return "📱 لم يتم العثور على أي منشورات حديثة."

        posts = result.data
        summary_parts = ["📲 **آخر منشورات الوسائط الاجتماعية (Ayrshare):**\n"]

        platform_icons = {
            "instagram": "📸",
            "tiktok": "🎵",
            "twitter": "🐦",
            "facebook": "👥",
            "linkedin": "💼"
        }

        for post in posts:
            created_at = post.get("created_at", "")
            content = post.get("content", "لا يوجد محتوى")
            engagement = post.get("engagement", "؟")
            reach = post.get("reach", "؟")
            platforms = post.get("platforms") or []

            try:
                date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d")
            except:
                date = "تاريخ غير معروف"

            formatted_platforms = ", ".join([f"{platform_icons.get(p, '🌐')} {p}" for p in platforms])

            summary_parts.append(
                f"• **{date}** | {formatted_platforms}\n"
                f"  - ✍️ المحتوى: {content[:100]}{'...' if len(content) > 100 else ''}\n"
                f"  - 👥 التفاعل: {engagement}\n"
                f"  - 👀 الوصول: {reach}\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching posts: {e}")
        return "⚠️ عذراً، حدث خطأ أثناء جلب بيانات المنشورات الاجتماعية."
