#!/usr/bin/env python3
"""
Test script to check onboarding endpoints
"""

import requests
import json

def test_onboarding_endpoints():
    base_url = "http://localhost:8000"  # Change this to your Render URL if testing deployed version
    
    print("🧪 Testing Onboarding Endpoints")
    print("=" * 50)
    
    # Test 1: Start onboarding
    print("\n1. Testing /onboarding/start")
    try:
        response = requests.post(
            f"{base_url}/onboarding/start",
            json={"user_id": "test_user_123"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Continue onboarding
    print("\n2. Testing /onboarding/step")
    try:
        response = requests.post(
            f"{base_url}/onboarding/step",
            json={"user_id": "test_user_123", "value": "أحمد"},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Check profile status
    print("\n3. Testing /profile/status")
    try:
        response = requests.get(
            f"{base_url}/profile/status?user_id=test_user_123"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_onboarding_endpoints()
