from datetime import datetime

def format_date(date_str: str | None) -> str:
    """Format date string or return 'تاريخ غير معروف'."""
    if not date_str:
        return "تاريخ غير معروف"
    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except:
        return "تاريخ غير معروف"

def format_social_post(post: dict) -> str:
    """
    Format a social media post into a readable string.
    """
    platform = post.get("platform", "منصة غير معروفة")
    date = format_date(post.get("published_date"))
    content = post.get("content", "لا يوجد محتوى")
    reach = post.get("reach", 0)
    ctr = post.get("ctr", 0)
    
    platform_icons = {
        "instagram": "📸",
        "tiktok": "🎵",
        "twitter": "🐦",
        "facebook": "👥",
        "linkedin": "💼"
    }
    icon = platform_icons.get(platform.lower(), "🌐")

    return (
        f"{icon} {platform} | {date}\n"
        f"📝 {content[:100]}...\n"
        f"👥 الوصول: {reach:,} مشاهدة\n"
        f"🎯 نسبة النقر: {ctr:.1f}%"
    )

def format_mention(mention: dict) -> str:
    """
    Format a brand mention into a readable string.
    """
    platform = mention.get("platform", "منصة غير معروفة")
    date = format_date(mention.get("published_date"))
    author = mention.get("author", "مجهول")
    text = mention.get("mention_text", "لا يوجد نص")
    sentiment = mention.get("sentiment", "محايد")
    score = mention.get("sentiment_score", 0)
    engagement = mention.get("engagement", 0)

    sentiment_ar = {
        "positive": "إيجابي ✨",
        "negative": "سلبي ⚠️",
        "neutral": "محايد 📝"
    }.get(sentiment, "غير معروف ❓")

    score_icon = "🟢" if score > 0.3 else "🔴" if score < -0.3 else "⚪"

    return (
        f"📅 {date} | {platform}\n"
        f"👤 {author}\n"
        f"💬 {text[:100]}...\n"
        f"📊 {sentiment_ar} {score_icon}\n"
        f"👥 تفاعل: {engagement:,}"
    )

def format_seo_signal(signal: dict) -> str:
    """
    Format an SEO signal into a readable string.
    """
    keyword = signal.get("keyword", "كلمة غير معروفة")
    position = signal.get("position", "غير معروف")
    volume = signal.get("volume", 0)
    cpc = signal.get("cpc", 0.0)
    competition = signal.get("competition", 0)

    competition_level = (
        "عالية 🔴" if competition > 0.66 else
        "متوسطة 🟡" if competition > 0.33 else
        "منخفضة 🟢"
    )

    return (
        f"🔑 {keyword}\n"
        f"📊 الموقع: {position}\n"
        f"🔍 حجم البحث: {volume:,}\n"
        f"💰 تكلفة النقرة: ${cpc:.2f}\n"
        f"⚔️ المنافسة: {competition_level}"
    )