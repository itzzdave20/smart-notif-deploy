"""
Test script for AI Chatbot API
Run this to test the API endpoints
"""

import requests
import json
import sys

API_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_status():
    """Test status endpoint"""
    print("\nTesting /api/status endpoint...")
    try:
        response = requests.get(f"{API_URL}/api/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat():
    """Test chat endpoint"""
    print("\nTesting /api/chat endpoint...")
    try:
        payload = {
            "message": "Hello! What is Python?",
            "conversation_history": [],
            "user_id": "test_user",
            "role": "student"
        }
        
        response = requests.post(
            f"{API_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            print(f"\n✅ Chat response received!")
            print(f"   Source: {result.get('source', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0)}")
            if result.get('model'):
                print(f"   Model: {result.get('model')}")
            return True
        else:
            print(f"\n❌ Chat failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_conversation():
    """Test conversation with history"""
    print("\nTesting conversation with history...")
    try:
        # First message
        payload1 = {
            "message": "My name is Alice",
            "conversation_history": []
        }
        
        response1 = requests.post(f"{API_URL}/api/chat", json=payload1)
        result1 = response1.json()
        
        print(f"First message response: {result1.get('response', '')[:100]}...")
        
        # Second message with history
        payload2 = {
            "message": "What's my name?",
            "conversation_history": [
                {"role": "user", "content": "My name is Alice"},
                {"role": "assistant", "content": result1.get('response', '')}
            ]
        }
        
        response2 = requests.post(f"{API_URL}/api/chat", json=payload2)
        result2 = response2.json()
        
        print(f"Second message response: {result2.get('response', '')[:100]}...")
        
        return response2.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 50)
    print("AI Chatbot API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{API_URL}/health", timeout=2)
    except:
        print(f"\n❌ Cannot connect to API server at {API_URL}")
        print("   Make sure the server is running:")
        print("   python ai_chatbot_api.py")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Status Check", test_status()))
    results.append(("Chat Test", test_chat()))
    results.append(("Conversation Test", test_conversation()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

