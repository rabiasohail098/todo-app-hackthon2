#!/bin/bash
#
# Simple Load Test Script for Todo App
# Uses curl for basic load testing (alternative to k6)
#
# Usage: ./scripts/load-test.sh [OPTIONS]
#
# Options:
#   -u, --url       Base URL (default: http://localhost:8000)
#   -t, --token     JWT token for authentication
#   -c, --concurrent Number of concurrent requests (default: 10)
#   -n, --requests  Total number of requests (default: 100)
#   -h, --help      Show this help message
#

set -e

# Default values
BASE_URL="${BASE_URL:-http://localhost:8000}"
JWT_TOKEN="${JWT_TOKEN:-}"
CONCURRENT=10
TOTAL_REQUESTS=100

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -u|--url)
      BASE_URL="$2"
      shift 2
      ;;
    -t|--token)
      JWT_TOKEN="$2"
      shift 2
      ;;
    -c|--concurrent)
      CONCURRENT="$2"
      shift 2
      ;;
    -n|--requests)
      TOTAL_REQUESTS="$2"
      shift 2
      ;;
    -h|--help)
      head -20 "$0" | tail -18
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    Todo App Load Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Base URL:    $BASE_URL"
echo "  Concurrent:  $CONCURRENT"
echo "  Total:       $TOTAL_REQUESTS"
echo "  Token:       ${JWT_TOKEN:+Provided}${JWT_TOKEN:-Not provided}"
echo ""

# Check if API is accessible
echo -e "${YELLOW}Checking API health...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" 2>/dev/null || echo "000")
if [ "$HEALTH_STATUS" != "200" ]; then
  echo -e "${RED}ERROR: API is not accessible (status: $HEALTH_STATUS)${NC}"
  exit 1
fi
echo -e "${GREEN}API is healthy!${NC}"
echo ""

# Prepare headers
HEADERS="-H 'Content-Type: application/json'"
if [ -n "$JWT_TOKEN" ]; then
  HEADERS="$HEADERS -H 'Authorization: Bearer $JWT_TOKEN'"
fi

# Results tracking
SUCCESS=0
FAILED=0
TOTAL_TIME=0

# Function to make a request and track results
make_request() {
  local method=$1
  local endpoint=$2
  local data=$3
  local expected_status=$4

  local start_time=$(date +%s%3N)
  local cmd="curl -s -o /dev/null -w '%{http_code}' -X $method $HEADERS"

  if [ -n "$data" ]; then
    cmd="$cmd -d '$data'"
  fi

  cmd="$cmd '$BASE_URL$endpoint'"

  local status=$(eval $cmd 2>/dev/null || echo "000")
  local end_time=$(date +%s%3N)
  local duration=$((end_time - start_time))

  TOTAL_TIME=$((TOTAL_TIME + duration))

  if [ "$status" = "$expected_status" ] || [ "$status" = "200" ] || [ "$status" = "201" ] || [ "$status" = "204" ]; then
    SUCCESS=$((SUCCESS + 1))
    echo -n "."
  else
    FAILED=$((FAILED + 1))
    echo -n "x"
  fi
}

# Start load test
echo -e "${YELLOW}Running load test...${NC}"
START_TIME=$(date +%s)

# Run concurrent requests
for ((i=1; i<=TOTAL_REQUESTS; i++)); do
  # Health check
  make_request "GET" "/health" "" "200" &

  # List tasks (if token provided)
  if [ -n "$JWT_TOKEN" ]; then
    make_request "GET" "/api/tasks" "" "200" &
  fi

  # Wait for concurrent batch
  if [ $((i % CONCURRENT)) -eq 0 ]; then
    wait
    echo ""
  fi
done

wait
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    RESULTS${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "  Total Requests: $((SUCCESS + FAILED))"
echo -e "  ${GREEN}Successful: $SUCCESS${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo "  Duration: ${DURATION}s"
echo "  Requests/sec: $(echo "scale=2; ($SUCCESS + $FAILED) / $DURATION" | bc)"
echo "  Avg Response Time: $(echo "scale=2; $TOTAL_TIME / ($SUCCESS + $FAILED)" | bc)ms"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}All tests passed!${NC}"
  exit 0
else
  echo -e "${YELLOW}Some tests failed. Check your setup.${NC}"
  exit 1
fi
