#!/usr/bin/env python3
"""
Test script to check deployment status
"""

import requests
import json

def test_deployment():
    # Try different possible URLs
    urls = [
        "https://mona-agent.onrender.com",
        "http://localhost:8000"  # for local testing
    ]
    
    print("🧪 Testing Deployment")
    print("=" * 50)
    
    for base_url in urls:
        print(f"\nTesting: {base_url}")
        
        # Test 1: Check if server is running
        try:
            response = requests.get(f"{base_url}/diag", timeout=10)
            print(f"✅ Server is running (Status: {response.status_code})")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   - Has Supabase: {data.get('has_supabase', 'Unknown')}")
                print(f"   - Endpoints: {data.get('endpoints', [])}")
                print(f"   - Chat test: {data.get('chat_test', 'Unknown')[:100]}...")
        except Exception as e:
            print(f"❌ Server not accessible: {e}")
            continue
        
        # Test 2: Check onboarding endpoints
        print(f"\nTesting onboarding endpoints on {base_url}")
        try:
            # Test start onboarding
            response = requests.post(
                f"{base_url}/onboarding/start",
                json={"user_id": "test_user_deployment"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"✅ /onboarding/start: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   - Message: {data.get('message', 'No message')[:50]}...")
                print(f"   - UI type: {data.get('ui_type', 'Unknown')}")
        except Exception as e:
            print(f"❌ /onboarding/start failed: {e}")
        
        try:
            # Test profile status
            response = requests.get(
                f"{base_url}/profile/status?user_id=test_user_deployment",
                timeout=10
            )
            print(f"✅ /profile/status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   - Has profile: {data.get('has_profile', 'Unknown')}")
        except Exception as e:
            print(f"❌ /profile/status failed: {e}")

if __name__ == "__main__":
    test_deployment()
