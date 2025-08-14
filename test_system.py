#!/usr/bin/env python3
"""
Simple test script to verify MORVO system components are working.
"""

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from onboarding_graph import start_onboarding, resume_onboarding
        print("✅ Onboarding graph imported successfully")
    except Exception as e:
        print(f"❌ Failed to import onboarding_graph: {e}")
        return False
    
    try:
        from agent import route_query, answer_with_openai
        print("✅ Agent module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import agent: {e}")
        return False
    
    try:
        from tools.supabase_client import supabase
        print("✅ Supabase client imported successfully")
    except Exception as e:
        print(f"❌ Failed to import supabase_client: {e}")
        return False
    
    try:
        from tools.openai_insights_tool import fetch_openai_insight
        print("✅ OpenAI insights tool imported successfully")
    except Exception as e:
        print(f"❌ Failed to import openai_insights_tool: {e}")
        return False
    
    return True

def test_onboarding():
    """Test onboarding system."""
    print("\n🔍 Testing onboarding system...")
    
    try:
        from onboarding_graph import start_onboarding, resume_onboarding
        
        # Test starting onboarding
        result = start_onboarding("test_user_123")
        print(f"✅ Onboarding start: {result.get('done', False)}")
        
        # Test first step
        step_result = resume_onboarding("test_user_123", "أحمد")
        print(f"✅ Onboarding step: {step_result.get('done', False)}")
        
        return True
    except Exception as e:
        print(f"❌ Onboarding test failed: {e}")
        return False

def test_agent():
    """Test agent routing."""
    print("\n🔍 Testing agent routing...")
    
    try:
        from agent import route_query
        
        # Test routing for different query types
        test_queries = [
            "ما هي آخر الأخبار عن سمعة العلامة التجارية؟",
            "كيف أداء المنشورات على السوشيال ميديا؟",
            "ما هي نتائج SEO؟",
            "كيف يمكنني تحسين التسويق؟"
        ]
        
        for query in test_queries:
            result = route_query(query)
            if result:
                print(f"✅ Routed query: '{query[:30]}...' -> Data found")
            else:
                print(f"✅ Query: '{query[:30]}...' -> Will use OpenAI")
        
        return True
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_tools():
    """Test tool functions."""
    print("\n🔍 Testing tools...")
    
    try:
        from tools.seo_tool import fetch_seo_signals_summary
        from tools.mentions_tool import fetch_mentions_summary
        from tools.posts_tool import fetch_posts_summary
        
        # Test SEO tool
        seo_result = fetch_seo_signals_summary()
        print(f"✅ SEO tool: {len(seo_result)} characters")
        
        # Test mentions tool
        mentions_result = fetch_mentions_summary()
        print(f"✅ Mentions tool: {len(mentions_result)} characters")
        
        # Test posts tool
        posts_result = fetch_posts_summary()
        print(f"✅ Posts tool: {len(posts_result)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 MORVO System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_onboarding,
        test_agent,
        test_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
