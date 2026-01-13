# Quickstart: Testing Error Handling and Stability Improvements

**Feature**: Error Handling and Stability Improvements
**Date**: 2026-01-03

## Prerequisites

- Node.js 20+ installed (frontend requires this to start)
- Backend running on http://localhost:8000
- Frontend running on http://localhost:3000
- React DevTools browser extension (for verifying no infinite loops)

---

## Test Scenario 1: Frontend Loads Without Infinite Loops

**Goal**: Verify that TagInput, TaskFilters, and TaskForm components render exactly once on mount.

**Steps**:
1. Open browser and navigate to http://localhost:3000
2. Open React DevTools → Profiler tab
3. Click "Record" button
4. Navigate to dashboard page
5. Stop recording after 3 seconds
6. Inspect the profiler flamegraph

**Expected Result**:
- ✅ TagInput component renders ONCE
- ✅ TaskFilters component renders ONCE
- ✅ TaskForm component renders ONCE
- ✅ No console errors in browser DevTools
- ✅ No "Warning: Cannot update component while rendering" warnings

**Failure Indicators**:
- ❌ Component shows multiple render bars in profiler
- ❌ Console shows "Maximum update depth exceeded"
- ❌ Page becomes unresponsive or freezes

---

## Test Scenario 2: Graceful API Error Handling (Backend Down)

**Goal**: Verify user-friendly error messages appear when backend is unavailable.

**Steps**:
1. Stop the backend server (Ctrl+C in backend terminal)
2. Open browser and navigate to http://localhost:3000/dashboard
3. Observe the UI behavior

**Expected Result**:
- ✅ Loading spinner appears briefly (1-2 seconds)
- ✅ Error message appears: "Unable to load data. Please check your connection."
- ✅ "Retry" button is visible
- ✅ Page does NOT crash or show blank screen
- ✅ Other UI elements (sidebar, header) still work

**Failure Indicators**:
- ❌ Blank white screen
- ❌ Console shows "TypeError: Cannot read property of null"
- ❌ Technical error message like "HTTP 500" or "ECONNREFUSED"
- ❌ No retry option available

---

## Test Scenario 3: Retry Button Functionality

**Goal**: Verify retry button successfully re-attempts failed API calls.

**Steps**:
1. With backend stopped, load dashboard (error state should appear)
2. Start the backend server
3. Click the "Retry" button in the error message

**Expected Result**:
- ✅ "Retry" button changes to "Retrying..." and becomes disabled
- ✅ Loading spinner appears
- ✅ After 1-2 seconds, data loads successfully
- ✅ Error message disappears
- ✅ Tasks/categories/tags display correctly

**Failure Indicators**:
- ❌ Clicking retry does nothing
- ❌ Multiple rapid clicks trigger multiple requests
- ❌ Error persists even though backend is running

---

## Test Scenario 4: Database Connection Retry Logic

**Goal**: Verify backend retries database connections with exponential backoff.

**Steps**:
1. Edit `backend/.env` and set DATABASE_URL to an invalid value:
   ```
   DATABASE_URL=postgresql://invalid:invalid@invalid.com/invalid
   ```
2. Start the backend server and observe logs
3. Wait for ~7 seconds (total retry time)

**Expected Result**:
- ✅ Log shows: "⚠️ Database connection failed (attempt 1/3). Retrying in 1s..."
- ✅ Log shows: "⚠️ Database connection failed (attempt 2/3). Retrying in 2s..."
- ✅ Log shows: "⚠️ Database connection failed (attempt 3/3). Retrying in 4s..."
- ✅ Log shows: "❌ Database connection failed after 3 retries. Check DATABASE_URL."
- ✅ Server exits with error code 1
- ✅ Total time is approximately 7 seconds (1 + 2 + 4)

**Failure Indicators**:
- ❌ Immediate crash without retries
- ❌ Retries happen too fast (no delay)
- ❌ Infinite retry loop (never gives up)
- ❌ Cryptic error message like "OperationalError: could not connect to server"

---

## Test Scenario 5: Environment Variable Validation

**Goal**: Verify clear error messages for missing environment variables.

**Steps**:
1. Temporarily rename `backend/.env` to `backend/.env.backup`
2. Start the backend server
3. Observe error output

**Expected Result**:
- ✅ Error message: "❌ ERROR: DATABASE_URL environment variable is not set"
- ✅ Fix suggestion: "Fix: Add DATABASE_URL=your-value to your .env file"
- ✅ Server exits immediately (fail-fast)
- ✅ Same checks for JWT_SECRET, CORS_ORIGINS

**Failure Indicators**:
- ❌ Server starts but crashes later when trying to connect
- ❌ Generic error: "KeyError: 'DATABASE_URL'"
- ❌ No actionable guidance on how to fix

---

## Test Scenario 6: No Infinite Loops with Empty Arrays Fallback

**Goal**: Verify components handle empty data gracefully without crashing.

**Steps**:
1. With backend stopped, load dashboard
2. Observe TaskFilters and TaskForm components
3. Check console for errors

**Expected Result**:
- ✅ Categories dropdown shows "No categories yet" (not crashing)
- ✅ Tags list shows "No tags yet" (not crashing)
- ✅ Priority dropdown still works
- ✅ No console errors about "Cannot read property 'map' of null"

**Failure Indicators**:
- ❌ TypeError: Cannot read property 'map' of null
- ❌ Component shows blank space instead of error message
- ❌ Infinite loading state

---

## Test Scenario 7: User-Friendly Error Messages

**Goal**: Verify technical errors are translated to user-friendly messages.

**Steps**:
1. Open browser DevTools Network tab
2. With backend running, load dashboard
3. In Network tab, right-click `/api/tasks` request → Block request URL
4. Refresh the page

**Expected Result**:
- ✅ Error message: "Unable to connect to server. Please check your connection."
- ✅ NO technical details like "net::ERR_BLOCKED_BY_CLIENT"
- ✅ NO stack traces visible to user

**Failure Indicators**:
- ❌ Raw error: "TypeError: Failed to fetch"
- ❌ Stack trace displayed in UI
- ❌ HTTP status codes shown to user (500, 404, etc.)

---

## Performance Benchmarks

After implementing all fixes, verify:

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Frontend load time | <3 seconds | Chrome DevTools → Performance tab |
| Component re-renders | ≤1 per user action | React DevTools → Profiler |
| Backend startup (normal) | <5 seconds | Time between `uvicorn` command and "Application startup complete" log |
| Backend startup (2 retries) | <15 seconds | Time with simulated database delay |
| ESLint warnings | 0 exhaustive-deps warnings | Run `npm run lint` in frontend |

---

## Quick Regression Test Checklist

Run this checklist after implementing fixes to ensure nothing broke:

- [ ] Dashboard loads without errors
- [ ] Can create a new task
- [ ] Can mark task as complete
- [ ] Can delete a task
- [ ] Categories dropdown works
- [ ] Tags input works
- [ ] Priority selector works
- [ ] Search bar filters tasks
- [ ] No infinite loops (check React DevTools)
- [ ] No console errors (check browser console)
- [ ] Backend starts successfully (check terminal logs)
- [ ] Database connection works (check logs)

---

## Debugging Tips

**If frontend still shows 500 errors**:
1. Check if backend is actually running: `curl http://localhost:8000/health`
2. Check browser console for actual error message
3. Check Network tab to see which endpoint is failing
4. Verify API_URL in frontend .env.local matches backend URL

**If infinite loops persist**:
1. Open React DevTools → Profiler
2. Record a session where the loop occurs
3. Find the component with many render bars
4. Check its useEffect hooks for missing or incorrect dependencies
5. Use `console.log()` to trace when effects run

**If backend won't start**:
1. Check .env file exists and has DATABASE_URL
2. Test database connection manually: `psql $DATABASE_URL`
3. Check logs for specific error (timeout vs auth vs DNS)
4. Verify Neon database is not paused (free tier auto-pauses after inactivity)

**If retry logic doesn't work**:
1. Check logs show "Retrying in Ns..." messages
2. Verify delays are actually exponential (1s, 2s, 4s)
3. Ensure max 3 attempts before giving up
4. Check error message includes actionable guidance

---

## Success Criteria Verification

| Success Criterion | Test Method | Status |
|------------------|-------------|--------|
| SC-001: Frontend loads in <3s | Performance tab | [ ] PASS / [ ] FAIL |
| SC-002: No component re-renders >1 time | React Profiler | [ ] PASS / [ ] FAIL |
| SC-003: 0 ESLint exhaustive-deps warnings | `npm run lint` | [ ] PASS / [ ] FAIL |
| SC-004: Error message in <2s when backend down | Manual timing | [ ] PASS / [ ] FAIL |
| SC-005: Retry button works | Manual test | [ ] PASS / [ ] FAIL |
| SC-006: Backend starts in <15s with retries | Terminal logs | [ ] PASS / [ ] FAIL |
| SC-007: Missing env var error in <1s | Terminal test | [ ] PASS / [ ] FAIL |
| SC-008: 100% fetch calls have try-catch | Code review | [ ] PASS / [ ] FAIL |
| SC-009: App works when backend down | Manual test | [ ] PASS / [ ] FAIL |
| SC-010: No stack traces in user-facing errors | Manual test | [ ] PASS / [ ] FAIL |

---

## Ready for Production?

**Checklist before merging**:
- [ ] All 10 success criteria pass
- [ ] No regressions in existing functionality
- [ ] All tests in quickstart.md pass
- [ ] Code review completed
- [ ] Documentation updated (README, STARTUP_GUIDE)
- [ ] Performance benchmarks meet targets
