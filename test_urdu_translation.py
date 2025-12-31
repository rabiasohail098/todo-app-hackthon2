"""Test Urdu translation functionality in chat agent."""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir / "src"))

from dotenv import load_dotenv

# Load environment
env_path = backend_dir / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(env_path, override=True)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from agent.chat_agent import ChatAgent


def get_test_session() -> Session:
    """Create test database session."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment")

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


async def test_translation():
    """Test Urdu translation with various messages."""
    session = get_test_session()
    user_id = "test-user-urdu"

    print("\n" + "=" * 70)
    print("🧪 TESTING URDU TRANSLATION FUNCTIONALITY")
    print("=" * 70)

    # Test 1: Create agent with Urdu language
    print("\n📝 Test 1: Creating agent with Urdu language...")
    agent = ChatAgent(session, user_id, language="ur")

    print(f"   ✓ Agent created")
    print(f"   Language: {agent.language}")
    print(f"   API Key: {agent.api_key[:30] if agent.api_key else 'MISSING'}...")
    print(f"   Model: {agent.model}")

    # Test 2: Send simple greeting
    print("\n📝 Test 2: Sending simple greeting in Urdu...")
    message1 = "سلام"
    print(f"   User: {message1}")

    try:
        result1 = await agent.process_message(message1)
        print(f"   Response Type: {result1.get('type')}")
        print(f"   Response: {result1.get('content')[:100]}...")

        # Check if response contains Urdu
        has_urdu = any(ord(c) > 1536 and ord(c) < 1791 for c in result1.get('content', ''))
        has_english = any(c.isascii() and c.isalpha() for c in result1.get('content', ''))

        print(f"   Has Urdu characters: {has_urdu}")
        print(f"   Has English characters: {has_english}")

        if has_urdu:
            print("   ✅ PASS: Response contains Urdu text")
        else:
            print("   ❌ FAIL: Response does not contain Urdu text")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 3: Create task in Urdu
    print("\n📝 Test 3: Creating task with Urdu request...")
    message2 = "ایک ٹاسک بنائیں دودھ خریدنا"
    print(f"   User: {message2}")

    try:
        result2 = await agent.process_message(message2)
        print(f"   Response Type: {result2.get('type')}")
        print(f"   Response: {result2.get('content')[:100]}...")

        # Check for task creation
        if "task" in result2:
            print(f"   Task Created: {result2['task']}")

        # Check if response contains Urdu
        has_urdu = any(ord(c) > 1536 and ord(c) < 1791 for c in result2.get('content', ''))

        if has_urdu:
            print("   ✅ PASS: Task creation response in Urdu")
        else:
            print("   ❌ FAIL: Task creation response not in Urdu")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 4: List tasks in Urdu
    print("\n📝 Test 4: Listing tasks with Urdu request...")
    message3 = "میرے تمام ٹاسک دکھائیں"
    print(f"   User: {message3}")

    try:
        result3 = await agent.process_message(message3)
        print(f"   Response Type: {result3.get('type')}")
        print(f"   Response: {result3.get('content')[:200]}...")

        # Check if response contains Urdu
        has_urdu = any(ord(c) > 1536 and ord(c) < 1791 for c in result3.get('content', ''))

        if has_urdu:
            print("   ✅ PASS: List tasks response in Urdu")
        else:
            print("   ❌ FAIL: List tasks response not in Urdu")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    # Test 5: English language agent for comparison
    print("\n📝 Test 5: Creating English agent for comparison...")
    agent_en = ChatAgent(session, user_id, language="en")

    message4 = "hello"
    print(f"   User (English): {message4}")

    try:
        result4 = await agent_en.process_message(message4)
        print(f"   Response Type: {result4.get('type')}")
        print(f"   Response: {result4.get('content')[:100]}...")

        # Check if response is in English
        has_english = any(c.isascii() and c.isalpha() for c in result4.get('content', ''))

        if has_english:
            print("   ✅ PASS: English agent responds in English")
        else:
            print("   ❌ FAIL: English agent not responding in English")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    print("\n" + "=" * 70)
    print("🏁 TRANSLATION TESTS COMPLETE")
    print("=" * 70)

    session.close()


async def test_translation_function_directly():
    """Test the translation function directly."""
    session = get_test_session()
    user_id = "test-user-direct"

    print("\n" + "=" * 70)
    print("🧪 TESTING DIRECT TRANSLATION FUNCTION")
    print("=" * 70)

    agent = ChatAgent(session, user_id, language="ur")

    # Test direct translation
    english_text = "Task created successfully"
    print(f"\n📝 Translating: '{english_text}'")

    try:
        urdu_text = await agent._translate_to_urdu(english_text)
        print(f"   Translation: {urdu_text}")

        # Check if translation contains Urdu
        has_urdu = any(ord(c) > 1536 and ord(c) < 1791 for c in urdu_text)

        if has_urdu:
            print("   ✅ PASS: Translation contains Urdu characters")
        else:
            print("   ❌ FAIL: Translation does not contain Urdu characters")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

    print("\n" + "=" * 70)

    session.close()


if __name__ == "__main__":
    print("\n🚀 Starting Urdu Translation Tests...\n")

    # Run tests
    asyncio.run(test_translation_function_directly())
    asyncio.run(test_translation())

    print("\n✅ All tests completed!\n")
