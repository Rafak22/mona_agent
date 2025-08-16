#!/usr/bin/env python3
"""
Test script for MORVO Streamlit application
"""

import os
import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        "streamlit",
        "schema",
        "memory_store", 
        "tools.conversation_logger",
        "onboarding_graph",
        "agent",
        "tools.supabase_client"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} modules")
        return False
    
    print("✅ All imports successful")
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing environment variables...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} (not set)")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing {len(missing_vars)} environment variables")
        print("   This is okay for testing, but required for full functionality")
        return False
    
    print("✅ All environment variables set")
    return True

def test_streamlit_app():
    """Test if the Streamlit app can be imported"""
    print("\n📱 Testing Streamlit app import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Import the app
        import streamlit_app
        print("✅ Streamlit app imported successfully")
        
        # Test if main function exists
        if hasattr(streamlit_app, 'main'):
            print("✅ Main function found")
        else:
            print("❌ Main function not found")
            return False
        
        # Test if chat function exists
        if hasattr(streamlit_app, 'chat_with_mona'):
            print("✅ Chat function found")
        else:
            print("❌ Chat function not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import Streamlit app: {e}")
        return False

def test_dependencies():
    """Test if all dependencies are installed"""
    print("\n📦 Testing dependencies...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    
    try:
        import openai
        print(f"✅ OpenAI {openai.__version__}")
    except ImportError:
        print("❌ OpenAI not installed")
        return False
    
    try:
        import supabase
        print("✅ Supabase")
    except ImportError:
        print("❌ Supabase not installed")
        return False
    
    try:
        import langchain
        print(f"✅ LangChain {langchain.__version__}")
    except ImportError:
        print("❌ LangChain not installed")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🤖 MORVO Streamlit Test Suite")
    print("=" * 40)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Streamlit App", test_streamlit_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Streamlit app is ready to run.")
        print("\nTo start the app:")
        print("  streamlit run streamlit_app.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 