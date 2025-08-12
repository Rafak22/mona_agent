import requests
import os
from tools.supabase_client import supabase

def debug_fetch_latest_seo():
    """
    Debug function to check Supabase connection and seo_signals table structure.
    """
    try:
        response = supabase.table("seo_signals").select("*").limit(1).execute()
        
        print("🔍 DEBUG: Supabase Response")
        print(f"Status: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
        
        if response.data:
            signal = response.data[0]
            print("✅ Found SEO signal data:")
            print(f"Available columns: {list(signal.keys())}")
            return {
                "success": True,
                "data": signal,
                "columns": list(signal.keys())
            }
        else:
            print("⚠️ No SEO signals found in database")
            return {
                "success": False,
                "error": "No SEO signals found in database"
            }
    except Exception as e:
        error_msg = f"🔥 Supabase Error: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def fetch_seo_signals_summary() -> str:
    """
    Fetches latest SEO metrics with detailed error reporting.
    Schema:
    - keyword: string
    - position: int
    - volume: int
    - cpc: float
    - competition: float
    """
    try:
        # First, run debug check
        debug_result = debug_fetch_latest_seo()
        if not debug_result["success"]:
            return f"⚠️ خطأ في الاتصال: {debug_result['error']}"

        # If debug successful, try actual fetch with correct columns
        available_columns = debug_result.get("columns", [])

        result = supabase.table("seo_signals") \
            .select(",".join(available_columns)) \
            .order("volume", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "📭 لم يتم العثور على أي تحليلات SEO حديثة."

        signals = result.data
        summary_parts = ["🔍 آخر تحليل لتحسين محركات البحث:\n"]

        for signal in signals:
            try:
                competition = signal.get("competition", 0)
                competition_level = (
                    "عالية 🔴" if competition > 0.66 else
                    "متوسطة 🟡" if competition > 0.33 else
                    "منخفضة 🟢"
                )
                
                summary_parts.append(
                    f"• الكلمة المفتاحية: {signal.get('keyword', '[غير معروف]')}\n"
                    f"  - الموقع: {signal.get('position', 'N/A')} 📊\n"
                    f"  - حجم البحث: {signal.get('volume', '0')} 🔍\n"
                    f"  - تكلفة النقرة: ${signal.get('cpc', '0.00'):.2f} 💰\n"
                    f"  - المنافسة: {competition_level}\n"
                )
            except Exception as signal_e:
                print(f"🔥 Error processing SEO signal: {signal_e}")
                print(f"Signal data: {signal}")
                summary_parts.append("⚠️ خطأ في معالجة هذه الكلمة المفتاحية")

        return "\n".join(summary_parts)

    except Exception as e:
        error_msg = f"🔥 Error fetching SEO signals: {str(e)}"
        print(error_msg)
        return f"❌ فشل في جلب بيانات SEO:\n{error_msg}"