from tools.mentions_tool import fetch_mentions_summary
from tools.posts_tool import fetch_posts_summary
from tools.seo_tool import fetch_seo_signals_summary
from schema import UserProfile
import re

def is_arabic(text: str) -> bool:
    """Quick check: does the string contain Arabic letters?"""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def route_query(message: str) -> str | None:
    """
    Routes queries to appropriate Supabase tools based on comprehensive keywords.
    Returns None if no match is found.
    """
    message = message.lower().strip()
    
    # ============================================
    # BRAND MENTIONS & REPUTATION KEYWORDS
    # ============================================
    mentions_keywords = [
        # Arabic - What people say variations
        "وش الناس يقولون", "وش يقول الناس", "وش يقولون", "يقولون عن", 
        "وش يقول", "ايش يقولون", "شنو يقولون", "كيف الناس يشوفون",
        
        # Arabic - Reputation & mentions
        "سمعة", "سمعتها", "سمعتهم", "ذكر", "يذكرون", "انطباع", "انطباعات",
        "رأي الناس", "آراء الناس", "تقييم الناس", "ردود الفعل",
        
        # Arabic - Social sentiment
        "تعليقات", "تعليقات الناس", "ردود", "مراجعات", "تقييمات",
        "شكاوى", "مدح", "انتقادات", "إيجابي", "سلبي", "محايد",
        
        # Arabic - Brand perception
        "صورة العلامة", "صورة الشركة", "نظرة الناس", "كيف يشوفونها",
        "ثقة العملاء", "ولاء العملاء", "حب العملاء",
        
        # English
        "brand mentions", "reputation", "sentiment", "what people say",
        "public opinion", "customer feedback", "reviews", "comments",
        "mentions", "brand perception", "image", "trust", "loyalty"
    ]
    
    if any(kw in message for kw in mentions_keywords):
        return fetch_mentions_summary()
    
    # ============================================
    # SOCIAL MEDIA POSTS & CONTENT KEYWORDS
    # ============================================
    posts_keywords = [
        # Arabic - Posts & content
        "بوست", "بوستات", "منشور", "منشورات", "محتوى", "محتويات",
        "مشاركة", "مشاركات", "نشر", "نشرت", "نشروا",
        
        # Arabic - Social media platforms
        "انستغرام", "انستا", "تويتر", "فيسبوك", "تيك توك", "سناب شات",
        "يوتيوب", "لينكد ان", "وسائل التواصل", "السوشيال ميديا",
        "التواصل الاجتماعي", "المنصات الاجتماعية",
        
        # Arabic - Engagement metrics
        "تفاعل", "تفاعلات", "إعجاب", "إعجابات", "لايك", "لايكات",
        "تعليق", "كومنت", "شير", "مشاركة", "ريتويت", "ريبوست",
        "مشاهدات", "ريتش", "وصول", "انتشار",
        
        # Arabic - Content types
        "صورة", "صور", "فيديو", "فيديوهات", "ريلز", "ستوري", "حملة",
        "حملات", "إعلان", "إعلانات", "كامبين", "كونتنت",
        
        # Arabic - Performance
        "أداء المنشورات", "نجاح المحتوى", "فشل المحتوى", "أفضل المنشورات",
        "أسوأ المنشورات", "أكثر تفاعل", "أقل تفاعل",
        
        # English
        "post", "posts", "social media", "content", "engagement", 
        "instagram", "twitter", "facebook", "tiktok", "youtube",
        "likes", "comments", "shares", "views", "reach", "impressions",
        "campaign", "campaigns", "advertisement", "ads", "reels", "stories"
    ]
    
    if any(kw in message for kw in posts_keywords):
        return fetch_posts_summary()
    
    # ============================================
    # SEO & KEYWORDS ANALYTICS
    # ============================================
    seo_keywords = [
        # Arabic - Keywords & SEO
        "كلمات مفتاحية", "كلمة مفتاحية", "كيوردز", "كلمات البحث",
        "بحث", "بحثوا", "يبحثون", "محركات البحث", "جوجل",
        
        # Arabic - Rankings & positions
        "ترتيب", "ترتيبات", "تتصدر", "تصدر", "رانكنج", "موقع",
        "مرتبة", "مركز", "الصفحة الأولى", "نتائج البحث",
        "ظهور في البحث", "فيندابيليتي",
        
        # Arabic - SEO metrics
        "زيارات", "زوار", "ترافيك", "نقرات", "كليكات", "معدل النقر",
        "معدل الارتداد", "وقت البقاء", "صفحات المشاهدة",
        
        # Arabic - SEO optimization
        "تحسين محركات البحث", "سيو", "أوبتيمايزيشن", "تهيئة",
        "فهرسة", "أرشفة", "كرولنج", "إندكسنج",
        
        # Arabic - Competition
        "منافسين", "منافسة", "مقارنة مع المنافسين", "موقع المنافسين",
        "أداء المنافسين", "تفوق على المنافسين",
        
        # Arabic - Website performance
        "موقع الشركة", "الموقع الإلكتروني", "سرعة الموقع", "أداء الموقع",
        "تجربة المستخدم", "يو إكس", "واجهة المستخدم",
        
        # English
        "seo", "keywords", "ranking", "search", "google", "search engine",
        "optimization", "rank", "position", "traffic", "visitors",
        "clicks", "ctr", "bounce rate", "indexing", "crawling",
        "serp", "search results", "organic", "competitors", "competition"
    ]
    
    if any(kw in message for kw in seo_keywords):
        return fetch_seo_signals_summary()
    
    # ============================================
    # GENERAL DATA & ANALYTICS KEYWORDS
    # ============================================
    general_data_keywords = [
        # Arabic - General analytics
        "تحليل", "تحليلات", "بيانات", "إحصائيات", "أرقام", "نتائج",
        "تقرير", "تقارير", "داشبورد", "لوحة المعلومات",
        "مؤشرات الأداء", "كي بي آي", "متريكس", "مقاييس",
        
        # Arabic - Performance questions
        "كيف الأداء", "أداء الشركة", "نجاح الشركة", "نتائج الحملات",
        "عائد الاستثمار", "آر أو آي", "ربحية", "مبيعات",
        
        # Arabic - Comparative analysis
        "مقارنة", "مقارنات", "أفضل", "أسوأ", "تحسن", "تراجع",
        "نمو", "انخفاض", "زيادة", "تطور", "تقدم",
        
        # English
        "analytics", "data", "statistics", "metrics", "performance",
        "report", "dashboard", "kpi", "roi", "analysis", "insights"
    ]
    
    # For general data questions, you might want to return a combined summary
    # or let it go to OpenAI for a more comprehensive response
    
    return None

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    """
    Simple routing: try Supabase tools first, then OpenAI fallback.
    """
    # Try Supabase tools first
    tool_response = route_query(message)
    if tool_response:
        return tool_response
    
    # OpenAI fallback for general questions
    try:
        # Import OpenAI here
        import openai
        import os
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مورفو، وكيلة تسويق ذكية متخصصة في تحليل بيانات المراعي. أجب باللغة العربية بطريقة ودودة ومفيدة."},
                {"role": "user", "content": message}
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback response
        return (
            f"مرحباً! شكراً لسؤالك '{message}'. أنا مورفو، وكيلتك التسويقية الذكية. "
            "يمكنني مساعدتك في تحليل البيانات التسويقية للمراعي!"
            if is_arabic(message) else
            f"Hello! Thanks for your question '{message}'. I'm MORVO, your smart marketing agent. "
            "I can help you analyze Almarai's marketing data!"
        )