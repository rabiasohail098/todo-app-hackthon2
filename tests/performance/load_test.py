"""
Performance/Load Testing Script using locust.

Run with: locust -f load_test.py --host=http://localhost:8000

Or for headless mode:
locust -f load_test.py --host=http://localhost:8000 --headless -u 100 -r 10 -t 5m
"""
import json
import random
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta


class TodoUser(HttpUser):
    """Simulates a user interacting with the Todo API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None
    user_id = None
    created_tasks = []

    def on_start(self):
        """Called when a simulated user starts."""
        # Create a unique user for this session
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        self.email = f"loadtest_{timestamp}@example.com"
        self.password = "TestPassword123!"

        # Note: In a real scenario, you'd register/login here
        # For now, we'll use a test JWT token approach
        self.headers = {
            "Content-Type": "application/json",
            # Add your test token here or implement login
            # "Authorization": f"Bearer {self.token}"
        }

    @task(10)
    def get_tasks(self):
        """GET /api/tasks - Most common operation."""
        with self.client.get(
            "/api/tasks",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - need valid token")
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(5)
    def create_task(self):
        """POST /api/tasks - Create a new task."""
        task_data = {
            "title": f"Load Test Task {random.randint(1000, 9999)}",
            "description": "Created during performance testing",
            "priority": random.choice(["low", "medium", "high", "critical"]),
            "is_completed": False,
        }

        with self.client.post(
            "/api/tasks",
            json=task_data,
            headers=self.headers,
            catch_response=True,
            name="/api/tasks [POST]"
        ) as response:
            if response.status_code in (200, 201):
                try:
                    data = response.json()
                    if "id" in data:
                        self.created_tasks.append(data["id"])
                    response.success()
                except:
                    response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized")
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(3)
    def update_task(self):
        """PATCH /api/tasks/{id} - Update a task."""
        if not self.created_tasks:
            return

        task_id = random.choice(self.created_tasks)
        update_data = {
            "title": f"Updated Task {random.randint(1000, 9999)}",
            "priority": random.choice(["low", "medium", "high"]),
        }

        with self.client.patch(
            f"/api/tasks/{task_id}",
            json=update_data,
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/{id} [PATCH]"
        ) as response:
            if response.status_code in (200, 204):
                response.success()
            elif response.status_code == 404:
                self.created_tasks.remove(task_id)
                response.success()  # Task was deleted elsewhere
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(2)
    def complete_task(self):
        """Mark a task as completed."""
        if not self.created_tasks:
            return

        task_id = random.choice(self.created_tasks)

        with self.client.patch(
            f"/api/tasks/{task_id}",
            json={"is_completed": True},
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/{id} [COMPLETE]"
        ) as response:
            if response.status_code in (200, 204):
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(1)
    def delete_task(self):
        """DELETE /api/tasks/{id} - Delete a task."""
        if not self.created_tasks:
            return

        task_id = self.created_tasks.pop(0)

        with self.client.delete(
            f"/api/tasks/{task_id}",
            headers=self.headers,
            catch_response=True,
            name="/api/tasks/{id} [DELETE]"
        ) as response:
            if response.status_code in (200, 204):
                response.success()
            elif response.status_code == 404:
                response.success()  # Already deleted
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(8)
    def get_statistics(self):
        """GET /api/statistics - Get task statistics."""
        with self.client.get(
            "/api/statistics",
            headers=self.headers,
            catch_response=True,
            name="/api/statistics"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(4)
    def get_categories(self):
        """GET /api/categories - Get categories."""
        with self.client.get(
            "/api/categories",
            headers=self.headers,
            catch_response=True,
            name="/api/categories"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(4)
    def get_tags(self):
        """GET /api/tags - Get tags."""
        with self.client.get(
            "/api/tags",
            headers=self.headers,
            catch_response=True,
            name="/api/tags"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")

    @task(2)
    def health_check(self):
        """GET /health - Health check endpoint."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


class HighLoadUser(HttpUser):
    """Simulates high-load scenarios with aggressive task creation."""

    wait_time = between(0.1, 0.5)  # Very short wait times

    @task
    def rapid_task_creation(self):
        """Rapidly create tasks to test system under load."""
        task_data = {
            "title": f"High Load Task {random.randint(1, 999999)}",
            "description": "Stress test task",
            "priority": "medium",
        }

        self.client.post("/api/tasks", json=task_data, name="/api/tasks [STRESS]")

    @task
    def rapid_reads(self):
        """Rapidly read tasks list."""
        self.client.get("/api/tasks", name="/api/tasks [STRESS READ]")


# Performance metrics collection
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Collect custom metrics on each request."""
    if response_time > 500:  # Log slow requests
        print(f"SLOW REQUEST: {name} took {response_time}ms")
