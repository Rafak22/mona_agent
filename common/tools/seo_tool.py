import requests
import os
from tools.supabase_client import supabase

def _check_seo_table_structure():
    """
    Internal function to check Supabase connection and seo_signals table structure.
    """
    try:
        response = supabase.table("seo_signals").select("*").limit(1).execute()
        
        if response.data:
            signal = response.data[0]
            return {
                "success": True,
                "data": signal,
                "columns": list(signal.keys())
            }
        else:
            return {
                "success": False,
                "error": "No SEO signals found in database"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Supabase Error: {str(e)}"
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
        # First, check table structure
        table_check = _check_seo_table_structure()
        if not table_check["success"]:
            return f"⚠️ خطأ في الاتصال: {table_check['error']}"

        # If check successful, try actual fetch with correct columns
        available_columns = table_check.get("columns", [])

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
                summary_parts.append("⚠️ خطأ في معالجة هذه الكلمة المفتاحية")

        return "\n".join(summary_parts)

    except Exception as e:
        return f"❌ فشل في جلب بيانات SEO: {str(e)}"