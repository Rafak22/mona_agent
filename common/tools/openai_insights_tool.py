import requests
import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# Initialize OpenAI client
llm = None
try:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_KEY:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=OPENAI_KEY
        )
    else:
        print("⚠️  OpenAI API key not found. AI features will be disabled.")
except Exception as e:
    print(f"⚠️  Failed to initialize OpenAI client: {e}")
    llm = None

@tool
def fetch_openai_insight(query: str, context: Optional[str] = None, profile_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Fetches real-time marketing insights using OpenAI Chat Completions.
    
    Args:
        query: The user's question or request for insights
        context: Additional context about the conversation or situation
        profile_data: User profile data for personalized responses
    
    Returns:
        A detailed marketing insight or recommendation
    """
    
    # Build a comprehensive system prompt
    system_prompt = """You are MORVO, a smart marketing assistant specializing in the Saudi market. 
    
    Your expertise includes:
    - Digital marketing strategies
    - Social media marketing
    - SEO and content marketing
    - Brand reputation management
    - Market analysis and insights
    - ROI optimization
    - Saudi market trends and cultural considerations
    
    Provide practical, actionable advice in Arabic. Be specific, data-driven when possible, 
    and consider the Saudi business context and cultural nuances.
    
    Always structure your response clearly and provide actionable next steps."""
    
    # Build the user message with context
    user_message = query
    
    if context:
        user_message = f"Context: {context}\n\nQuestion: {query}"
    
    if profile_data:
        profile_summary = "\n".join([f"{k}: {v}" for k, v in profile_data.items() if v])
        user_message = f"User Profile:\n{profile_summary}\n\n{user_message}"
    
    if llm is None:
        return "⚠️ خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى المحاولة لاحقاً."
    
    try:
        # Use the LangChain client for better error handling
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        return response.content
        
    except Exception as e:
        error_msg = f"🚨 حدث خطأ في جلب الرؤى: {str(e)}"
        
        # Provide fallback response based on error type
        if "rate limit" in str(e).lower() or "quota" in str(e).lower():
            return "⚠️ تم استنفاذ الحد المسموح من الطلبات. يرجى المحاولة بعد قليل."
        elif "timeout" in str(e).lower():
            return "⏰ انتهت مهلة الطلب. يرجى المحاولة مرة أخرى."
        elif "authentication" in str(e).lower() or "api key" in str(e).lower():
            return "🔑 خطأ في إعدادات API. يرجى التواصل مع الدعم الفني."
        else:
            return "❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى أو التواصل مع الدعم الفني."

@tool
def analyze_marketing_strategy(business_type: str, goals: List[str], budget: str, current_channels: Optional[List[str]] = None) -> str:
    """
    Analyzes and provides a comprehensive marketing strategy based on business profile.
    
    Args:
        business_type: Type of business (e.g., e-commerce, restaurant, service)
        goals: List of marketing goals
        budget: Budget range
        current_channels: Current marketing channels being used
    
    Returns:
        A detailed marketing strategy with recommendations
    """
    
    system_prompt = """You are a senior marketing strategist specializing in the Saudi market.
    
    Create comprehensive marketing strategies that consider:
    - Saudi consumer behavior and preferences
    - Local market trends and opportunities
    - Cultural and religious considerations
    - Digital adoption patterns in Saudi Arabia
    - Budget optimization for maximum ROI
    
    Provide specific, actionable recommendations with estimated costs and timelines."""
    
    user_message = f"""
    Business Type: {business_type}
    Goals: {', '.join(goals)}
    Budget: {budget}
    Current Channels: {', '.join(current_channels) if current_channels else 'None'}
    
    Please provide a comprehensive marketing strategy including:
    1. Recommended channels and platforms
    2. Content strategy
    3. Budget allocation
    4. Timeline and milestones
    5. Success metrics
    6. Cultural considerations for Saudi market
    """
    
    if llm is None:
        return "⚠️ خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى المحاولة لاحقاً."
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        return response.content
        
    except Exception as e:
        return f"❌ حدث خطأ في تحليل الاستراتيجية: {str(e)}"

@tool
def generate_content_ideas(content_type: str, industry: str, target_audience: str, platform: str) -> str:
    """
    Generates content ideas tailored for specific platforms and audiences.
    
    Args:
        content_type: Type of content (social media, blog, video, etc.)
        industry: Business industry
        target_audience: Target audience description
        platform: Platform (Instagram, LinkedIn, TikTok, etc.)
    
    Returns:
        A list of content ideas with descriptions
    """
    
    system_prompt = """You are a creative content strategist for the Saudi market.
    
    Generate engaging content ideas that:
    - Resonate with Saudi audiences
    - Consider cultural and religious sensitivities
    - Are optimized for the specified platform
    - Align with the business industry
    - Drive engagement and conversions
    
    Provide specific ideas with descriptions and hashtag suggestions."""
    
    user_message = f"""
    Content Type: {content_type}
    Industry: {industry}
    Target Audience: {target_audience}
    Platform: {platform}
    
    Please provide:
    1. 10-15 content ideas with descriptions
    2. Recommended hashtags for each idea
    3. Best posting times for the platform
    4. Engagement strategies
    5. Cultural considerations
    """
    
    if llm is None:
        return "⚠️ خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى المحاولة لاحقاً."
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        return response.content
        
    except Exception as e:
        return f"❌ حدث خطأ في توليد أفكار المحتوى: {str(e)}"

@tool
def analyze_competitor_strategy(competitor_name: str, industry: str, focus_areas: Optional[List[str]] = None) -> str:
    """
    Analyzes competitor strategies and provides insights.
    
    Args:
        competitor_name: Name of the competitor
        industry: Industry sector
        focus_areas: Specific areas to analyze (optional)
    
    Returns:
        Competitor analysis with actionable insights
    """
    
    system_prompt = """You are a competitive intelligence analyst for the Saudi market.
    
    Analyze competitors considering:
    - Saudi market positioning
    - Digital presence and strategy
    - Content and messaging approach
    - Customer engagement tactics
    - Market share and positioning
    - Opportunities for differentiation
    
    Provide actionable insights for competitive advantage."""
    
    focus_areas = focus_areas or ["digital presence", "content strategy", "customer engagement", "market positioning"]
    
    user_message = f"""
    Competitor: {competitor_name}
    Industry: {industry}
    Focus Areas: {', '.join(focus_areas)}
    
    Please provide:
    1. Digital presence analysis
    2. Content strategy insights
    3. Customer engagement tactics
    4. Market positioning analysis
    5. Opportunities for differentiation
    6. Recommendations for competitive advantage
    """
    
    if llm is None:
        return "⚠️ خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى المحاولة لاحقاً."
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        return response.content
        
    except Exception as e:
        return f"❌ حدث خطأ في تحليل المنافسين: {str(e)}"

@tool
def calculate_roi_metrics(campaign_cost: float, revenue_generated: float, campaign_duration: str, channel: str) -> str:
    """
    Calculates ROI metrics and provides optimization recommendations.
    
    Args:
        campaign_cost: Total campaign cost
        revenue_generated: Revenue generated from campaign
        campaign_duration: Duration of campaign
        channel: Marketing channel used
    
    Returns:
        ROI analysis with recommendations
    """
    
    try:
        # Calculate basic ROI
        roi = ((revenue_generated - campaign_cost) / campaign_cost) * 100
        profit = revenue_generated - campaign_cost
        
        # Determine ROI performance
        if roi >= 300:
            performance = "ممتاز"
            recommendation = "استمر في هذا النهج ووسع الحملة"
        elif roi >= 100:
            performance = "جيد"
            recommendation = "حسن الحملة للحصول على نتائج أفضل"
        elif roi >= 0:
            performance = "مقبول"
            recommendation = "تحسين استراتيجية الحملة ضروري"
        else:
            performance = "ضعيف"
            recommendation = "إعادة تقييم شاملة للحملة مطلوبة"
        
        analysis = f"""
📊 تحليل عائد الاستثمار (ROI)

💰 التكاليف: {campaign_cost:,.2f} ريال
💵 الإيرادات: {revenue_generated:,.2f} ريال
📈 الربح: {profit:,.2f} ريال
🎯 ROI: {roi:.1f}%

📊 الأداء: {performance}
💡 التوصية: {recommendation}

📋 تحليل مفصل:
• القناة: {channel}
• المدة: {campaign_duration}
• نسبة الربحية: {(profit/revenue_generated)*100:.1f}%

🔧 توصيات للتحسين:
1. تحليل نقاط القوة والضعف
2. اختبار استراتيجيات جديدة
3. تحسين استهداف الجمهور
4. مراقبة المنافسين
5. تحسين رسالة الحملة
        """
        
        return analysis
        
    except Exception as e:
        return f"❌ حدث خطأ في حساب ROI: {str(e)}"

# Legacy function for backward compatibility
def fetch_openai_insight_legacy(query: str) -> str:
    """Legacy function for backward compatibility"""
    return fetch_openai_insight(query)


