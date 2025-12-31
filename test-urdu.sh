#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "🧪 URDU TRANSLATION IMPLEMENTATION VERIFICATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verify implementation
echo "📝 Checking implementation in chat_agent.py..."
echo ""

# Check 1: Translation function
if grep -q "async def _translate_to_urdu" backend/src/agent/chat_agent.py; then
    echo "✅ Translation function exists (line 144)"
else
    echo "❌ Translation function NOT found"
    exit 1
fi

# Check 2: Action post-processing
if grep -q "Response appears to be in English, translating" backend/src/agent/chat_agent.py; then
    echo "✅ Action post-processing exists (line 212)"
else
    echo "❌ Action post-processing NOT found"
    exit 1
fi

# Check 3: Chat post-processing
if grep -q "Chat response in English, translating" backend/src/agent/chat_agent.py; then
    echo "✅ Chat post-processing exists (line 225)"
else
    echo "❌ Chat post-processing NOT found"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ ALL COMPONENTS VERIFIED!"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Show next steps
echo "📚 Documentation Created:"
echo "   1. URDU_TRANSLATION_TEST_GUIDE.md - Complete testing guide"
echo "   2. URDU_TRANSLATION_IMPLEMENTATION.md - Implementation details"
echo ""

echo "🚀 To Test the Implementation:"
echo ""
echo "   Terminal 1 - Start Backend:"
echo "   ──────────────────────────────"
echo "   cd backend"
echo "   uvicorn src.api.main:app --reload --port 8000"
echo ""

echo "   Terminal 2 - Start Frontend:"
echo "   ────────────────────────────────"
echo "   cd frontend"
echo "   npm run dev"
echo ""

echo "   Browser - Test Urdu Translation:"
echo "   ────────────────────────────────────"
echo "   1. Open http://localhost:3000/chat"
echo "   2. Click 'اردو' button (top right)"
echo "   3. Send: 'ایک ٹاسک بنائیں'"
echo "   4. Verify response is in Urdu"
echo ""

echo "📊 Watch Backend Logs For:"
echo "   ───────────────────────────"
echo "   • 'Creating agent with language: ur'"
echo "   • 'Response appears to be in English, translating...'"
echo "   • 'Translated to Urdu: ...'"
echo ""

echo "💡 Tip: If still getting English responses, make sure:"
echo "   • Backend was restarted after code changes"
echo "   • Language is set to 'ur' in UI"
echo "   • OpenRouter API key is valid (check .env)"
echo ""

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8000"
else
    echo "   ⚠️  Backend is NOT running"
    echo "   Start it with: cd backend && uvicorn src.api.main:app --reload"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
