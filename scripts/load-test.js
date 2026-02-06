/**
 * Load Test Script for Todo App
 *
 * Usage: k6 run scripts/load-test.js
 *
 * Prerequisites:
 * - Install k6: https://k6.io/docs/getting-started/installation/
 * - Set environment variables:
 *   - BASE_URL: Base URL of the API (default: http://localhost:8000)
 *   - JWT_TOKEN: Valid JWT token for authentication
 *
 * Example:
 *   k6 run -e BASE_URL=http://localhost:8000 -e JWT_TOKEN=your-token scripts/load-test.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const taskCreationTime = new Trend('task_creation_time');
const taskListTime = new Trend('task_list_time');
const taskUpdateTime = new Trend('task_update_time');
const taskDeleteTime = new Trend('task_delete_time');

// Test configuration
export const options = {
  stages: [
    // Ramp up
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 25 },   // Ramp up to 25 users
    { duration: '2m', target: 50 },   // Stay at 50 users for 2 minutes
    { duration: '1m', target: 25 },   // Ramp down to 25 users
    { duration: '30s', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.01'],    // Less than 1% of requests should fail
    errors: ['rate<0.05'],             // Less than 5% error rate
  },
};

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const JWT_TOKEN = __ENV.JWT_TOKEN || '';

// Headers with authentication
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${JWT_TOKEN}`,
};

// Generate random task data
function generateTask() {
  const titles = [
    'Review code changes',
    'Write documentation',
    'Fix bug in login',
    'Update dependencies',
    'Deploy to staging',
    'Run database migrations',
    'Write unit tests',
    'Review pull request',
    'Setup CI/CD pipeline',
    'Optimize queries',
  ];

  const descriptions = [
    'This is a high priority task',
    'Needs to be done before release',
    'Assigned by the team lead',
    'Part of the sprint goals',
    'Technical debt cleanup',
  ];

  return {
    title: titles[Math.floor(Math.random() * titles.length)] + ` #${Date.now()}`,
    description: descriptions[Math.floor(Math.random() * descriptions.length)],
  };
}

// Main test function
export default function () {
  let taskId = null;

  group('Health Check', () => {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health check status is 200': (r) => r.status === 200,
    });
    errorRate.add(res.status !== 200);
  });

  sleep(0.5);

  group('Task CRUD Operations', () => {
    // Create Task
    group('Create Task', () => {
      const taskData = generateTask();
      const startTime = Date.now();
      const res = http.post(
        `${BASE_URL}/api/tasks`,
        JSON.stringify(taskData),
        { headers }
      );
      taskCreationTime.add(Date.now() - startTime);

      const success = check(res, {
        'create task status is 201': (r) => r.status === 201,
        'create task has id': (r) => {
          try {
            const body = JSON.parse(r.body);
            taskId = body.id;
            return taskId !== undefined;
          } catch {
            return false;
          }
        },
      });
      errorRate.add(!success);
    });

    sleep(0.3);

    // List Tasks
    group('List Tasks', () => {
      const startTime = Date.now();
      const res = http.get(`${BASE_URL}/api/tasks`, { headers });
      taskListTime.add(Date.now() - startTime);

      const success = check(res, {
        'list tasks status is 200': (r) => r.status === 200,
        'list tasks returns array': (r) => {
          try {
            const body = JSON.parse(r.body);
            return Array.isArray(body);
          } catch {
            return false;
          }
        },
      });
      errorRate.add(!success);
    });

    sleep(0.3);

    // Update Task (if created successfully)
    if (taskId) {
      group('Update Task', () => {
        const startTime = Date.now();
        const res = http.patch(
          `${BASE_URL}/api/tasks/${taskId}`,
          JSON.stringify({ is_completed: true }),
          { headers }
        );
        taskUpdateTime.add(Date.now() - startTime);

        const success = check(res, {
          'update task status is 200': (r) => r.status === 200,
        });
        errorRate.add(!success);
      });

      sleep(0.3);

      // Delete Task
      group('Delete Task', () => {
        const startTime = Date.now();
        const res = http.del(
          `${BASE_URL}/api/tasks/${taskId}`,
          null,
          { headers }
        );
        taskDeleteTime.add(Date.now() - startTime);

        const success = check(res, {
          'delete task status is 204 or 200': (r) => r.status === 204 || r.status === 200,
        });
        errorRate.add(!success);
      });
    }
  });

  sleep(1);
}

// Lifecycle hooks
export function setup() {
  console.log('Starting load test...');
  console.log(`Target URL: ${BASE_URL}`);
  console.log(`JWT Token: ${JWT_TOKEN ? 'Provided' : 'Not provided (some tests will fail)'}`);

  // Verify API is accessible
  const res = http.get(`${BASE_URL}/health`);
  if (res.status !== 200) {
    throw new Error(`API is not accessible. Health check returned: ${res.status}`);
  }

  return { startTime: Date.now() };
}

export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(`Load test completed in ${duration.toFixed(2)} seconds`);
}

// Summary handler
export function handleSummary(data) {
  return {
    'specs/006-phase-4-kubernetes/load-test-report.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

// Text summary helper
function textSummary(data, options) {
  const lines = [];
  lines.push('\n' + '='.repeat(60));
  lines.push('LOAD TEST SUMMARY');
  lines.push('='.repeat(60) + '\n');

  // Request metrics
  if (data.metrics.http_reqs) {
    lines.push(`Total Requests: ${data.metrics.http_reqs.values.count}`);
    lines.push(`Requests/sec: ${data.metrics.http_reqs.values.rate.toFixed(2)}`);
  }

  if (data.metrics.http_req_duration) {
    const dur = data.metrics.http_req_duration.values;
    lines.push(`\nResponse Time:`);
    lines.push(`  Average: ${dur.avg.toFixed(2)}ms`);
    lines.push(`  Min: ${dur.min.toFixed(2)}ms`);
    lines.push(`  Max: ${dur.max.toFixed(2)}ms`);
    lines.push(`  p95: ${dur['p(95)'].toFixed(2)}ms`);
  }

  if (data.metrics.http_req_failed) {
    lines.push(`\nFailure Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%`);
  }

  // Custom metrics
  const customMetrics = ['task_creation_time', 'task_list_time', 'task_update_time', 'task_delete_time'];
  lines.push('\nCustom Metrics:');
  customMetrics.forEach(metric => {
    if (data.metrics[metric]) {
      const m = data.metrics[metric].values;
      lines.push(`  ${metric}: avg=${m.avg.toFixed(2)}ms, p95=${m['p(95)'].toFixed(2)}ms`);
    }
  });

  lines.push('\n' + '='.repeat(60));

  return lines.join('\n');
}
