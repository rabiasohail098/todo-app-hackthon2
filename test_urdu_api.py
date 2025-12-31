"""Test Urdu translation via API endpoint."""

import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os

# Load frontend .env for backend URL
frontend_env = Path(__file__).parent / "frontend" / ".env.local"
if frontend_env.exists():
    load_dotenv(frontend_env)

BACKEND_URL = os.getenv("NEXT_PUBLIC_BACKEND_URL", "http://localhost:8000")
print(f"Testing against backend: {BACKEND_URL}")

# Test token (you need a valid JWT token)
# For testing, we'll use the same mock user approach
AUTH_TOKEN = "mock-jwt-token-test-user"

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}


def test_urdu_translation():
    """Test Urdu translation through chat API."""
    print("\n" + "=" * 70)
    print("🧪 TESTING URDU TRANSLATION VIA API")
    print("=" * 70)

    # Test 1: Send message in Urdu
    print("\n📝 Test 1: Sending Urdu message with language='ur'...")

    payload = {
        "message": "سلام، ایک ٹاسک بنائیں",
        "language": "ur"
    }

    print(f"   Request: {json.dumps(payload, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat/",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Response Type: {data.get('type')}")
            print(f"   Response Text: {data.get('response')[:200]}...")

            # Check for Urdu characters (Arabic script range: U+0600 to U+06FF)
            response_text = data.get('response', '')
            has_urdu = any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in response_text)
            has_english = any(c.isascii() and c.isalpha() for c in response_text)

            print(f"\n   Analysis:")
            print(f"   - Contains Urdu characters: {has_urdu}")
            print(f"   - Contains English characters: {has_english}")

            if has_urdu:
                print("   ✅ PASS: Response contains Urdu text")
            else:
                print("   ❌ FAIL: Response does not contain Urdu text")
                print("   ⚠️  Translation fallback may not be working")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

    # Test 2: Create task in Urdu
    print("\n📝 Test 2: Creating task with Urdu language...")

    payload = {
        "message": "add task buy milk",
        "language": "ur"
    }

    print(f"   Request: {json.dumps(payload, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat/",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Response Type: {data.get('type')}")
            print(f"   Response Text: {data.get('response')[:200]}...")

            # Check for Urdu
            response_text = data.get('response', '')
            has_urdu = any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in response_text)

            if data.get('type') == 'task_created':
                print(f"   Task: {data.get('data', {}).get('task')}")

            if has_urdu:
                print("   ✅ PASS: Task creation response in Urdu")
            else:
                print("   ❌ FAIL: Task creation response not in Urdu")
                print(f"   Actual response: {response_text}")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

    # Test 3: English for comparison
    print("\n📝 Test 3: English message for comparison...")

    payload = {
        "message": "hello",
        "language": "en"
    }

    print(f"   Request: {json.dumps(payload)}")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat/",
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Response Type: {data.get('type')}")
            print(f"   Response Text: {data.get('response')[:200]}...")

            response_text = data.get('response', '')
            has_english = any(c.isascii() and c.isalpha() for c in response_text)

            if has_english:
                print("   ✅ PASS: English response works correctly")
            else:
                print("   ⚠️  WARNING: No English text in response")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

    print("\n" + "=" * 70)
    print("🏁 API TRANSLATION TESTS COMPLETE")
    print("=" * 70)
    print("\n💡 Tips:")
    print("   - If Urdu is not showing, check backend logs for translation messages")
    print("   - Look for: 'Response appears to be in English, translating...'")
    print("   - Or: 'Chat response in English, translating...'")
    print("   - Check that backend is running with latest code")
    print()


def check_backend_health():
    """Check if backend is running."""
    print("\n🔍 Checking backend health...")

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend is running at {BACKEND_URL}")
            return True
        else:
            print(f"   ❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to backend at {BACKEND_URL}")
        print(f"   Make sure backend is running: cd backend && uvicorn src.api.main:app --reload")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting API-based Urdu Translation Tests...\n")

    if check_backend_health():
        test_urdu_translation()
    else:
        print("\n❌ Backend is not running. Please start it first.\n")
