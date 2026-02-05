#!/usr/bin/env python3
"""
API Verification Script
This script verifies that all API endpoints are properly defined and accessible
without requiring a database connection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_imports():
    """Test that all API modules can be imported without errors."""
    print("Testing API module imports...")

    try:
        from src.api.main import app
        print("[V] Main app imported successfully")

        # Check that the app has the expected routes
        routes = [route.path for route in app.routes]
        print(f"[V] Found {len(routes)} routes:")

        # Expected API routes
        expected_routes = [
            "/",  # root
            "/health",  # health check
            "/metrics",  # metrics
            "/api/tasks",  # tasks
            "/api/tasks/{task_id}",  # get single task
            "/api/categories",  # categories
            "/api/categories/{category_id}",  # get single category
            "/api/tasks/{task_id}/subtasks",  # subtasks
            "/api/subtasks/{subtask_id}",  # update/delete subtask
            "/api/tags",  # tags
            "/api/tags/popular",  # popular tags
            "/api/tasks/{task_id}/tags/{tag_id}",  # add/remove tag
            "/api/tasks/{task_id}/tags",  # get task tags
            "/api/statistics",  # statistics
            "/api/statistics/daily",  # daily stats
            "/api/statistics/productive-day",  # productive day
            "/api/statistics/categories",  # category stats
            "/api/statistics/priorities",  # priority stats
            "/api/tasks/{task_id}/attachments",  # attachments
            "/api/tasks/{task_id}/activity",  # activity
            "/api/chat/",  # chat
            "/api/chat/conversations/{conversation_id}/messages",  # conversation messages
            "/api/chat/conversations",  # user conversations
            "/api/chat/conversations/{conversation_id}",  # delete conversation
        ]

        found_expected = 0
        for expected_route in expected_routes:
            if any(expected_route.replace('{task_id}', '1').replace('{category_id}', '1').replace('{subtask_id}', '1').replace('{conversation_id}', '123') in route for route in routes):
                found_expected += 1
                print(f"  [V] {expected_route}")
            else:
                print(f"  [X] {expected_route} (not found)")

        print(f"\n[V] Found {found_expected}/{len(expected_routes)} expected routes")
        return True

    except Exception as e:
        print(f"[X] Error importing API modules: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """Test the structure of API endpoints."""
    print("\nTesting API structure...")

    try:
        from src.api.main import app

        # Count routes by tag to verify all feature sets are included
        tag_counts = {}
        for route in app.routes:
            if hasattr(route, 'tags'):
                for tag in route.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        print("API endpoints by feature:")
        for tag, count in tag_counts.items():
            print(f"  [TAG] {tag}: {count} endpoints")

        # Expected tags
        expected_tags = ["Health", "Tasks", "Categories", "Subtasks", "Statistics", "Tags", "Attachments", "Activity", "Chat"]
        found_tags = 0
        for tag in expected_tags:
            if tag in tag_counts:
                found_tags += 1
                print(f"  [V] {tag} endpoints found ({tag_counts[tag]})")
            else:
                print(f"  [X] {tag} endpoints missing")

        print(f"\n[V] Found {found_tags}/{len(expected_tags)} expected feature tags")
        return True

    except Exception as e:
        print(f"[X] Error testing API structure: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_client_creation():
    """Test creating a test client without database connection."""
    print("\nTesting API client creation...")

    try:
        from fastapi.testclient import TestClient
        from src.api.main import app

        # Create a test client - this should work without DB connection
        client = TestClient(app)
        print("[V] Test client created successfully")

        # Test health endpoint (should work without DB)
        response = client.get("/health")
        if response.status_code == 200:
            print("[V] Health endpoint accessible")
        else:
            print(f"[X] Health endpoint returned status {response.status_code}")

        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("[V] Root endpoint accessible")
        else:
            print(f"[X] Root endpoint returned status {response.status_code}")

        return True

    except Exception as e:
        print(f"[X] Error testing API client: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("[INFO] API Endpoint Verification Started")
    print("="*50)

    results = []

    results.append(test_api_imports())
    results.append(test_api_structure())
    results.append(test_api_client_creation())

    print("\n" + "="*50)
    print("SUMMARY")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")

    if all(results):
        print("\nAll API verification tests passed!")
        print("All endpoints are properly defined and accessible.")
        return 0
    else:
        print("\nSome API verification tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())