/**
 * k6 Load Testing Script for Todo API
 *
 * Run with: k6 run k6_load_test.js
 *
 * Options:
 *   k6 run --vus 100 --duration 5m k6_load_test.js
 *   k6 run --vus 50 --iterations 1000 k6_load_test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const taskCreationTime = new Trend('task_creation_time');
const taskListTime = new Trend('task_list_time');
const tasksCreated = new Counter('tasks_created');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Spike to 200 users
    { duration: '1m', target: 100 },  // Scale back to 100
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests should be below 500ms
    errors: ['rate<0.1'],              // Error rate should be below 10%
    task_creation_time: ['p(95)<1000'], // Task creation p95 < 1s
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  const headers = {
    'Content-Type': 'application/json',
    // Add Authorization header if needed
    // 'Authorization': `Bearer ${__ENV.TOKEN}`,
  };

  group('Health Check', function () {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health check status is 200': (r) => r.status === 200,
    });
    errorRate.add(res.status !== 200);
  });

  group('List Tasks', function () {
    const start = Date.now();
    const res = http.get(`${BASE_URL}/api/tasks`, { headers });
    taskListTime.add(Date.now() - start);

    check(res, {
      'list tasks status is 200 or 401': (r) => r.status === 200 || r.status === 401,
    });
    errorRate.add(res.status >= 500);
  });

  group('Create Task', function () {
    const taskData = JSON.stringify({
      title: `K6 Load Test Task ${Date.now()}`,
      description: 'Created by k6 performance test',
      priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
      is_completed: false,
    });

    const start = Date.now();
    const res = http.post(`${BASE_URL}/api/tasks`, taskData, { headers });
    taskCreationTime.add(Date.now() - start);

    const success = check(res, {
      'create task status is 200 or 201': (r) => r.status === 200 || r.status === 201,
    });

    if (success) {
      tasksCreated.add(1);
    }
    errorRate.add(res.status >= 500);
  });

  group('Get Statistics', function () {
    const res = http.get(`${BASE_URL}/api/statistics`, { headers });
    check(res, {
      'statistics status is 200 or 401': (r) => r.status === 200 || r.status === 401,
    });
    errorRate.add(res.status >= 500);
  });

  group('Get Categories', function () {
    const res = http.get(`${BASE_URL}/api/categories`, { headers });
    check(res, {
      'categories status is 200 or 401': (r) => r.status === 200 || r.status === 401,
    });
    errorRate.add(res.status >= 500);
  });

  sleep(Math.random() * 2 + 1); // Random sleep between 1-3 seconds
}

// Setup function - runs once before the test
export function setup() {
  console.log(`Starting load test against ${BASE_URL}`);

  // Verify server is up
  const res = http.get(`${BASE_URL}/health`);
  if (res.status !== 200) {
    console.error('Server health check failed!');
  }

  return { startTime: Date.now() };
}

// Teardown function - runs once after the test
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(`Load test completed in ${duration.toFixed(2)} seconds`);
}
