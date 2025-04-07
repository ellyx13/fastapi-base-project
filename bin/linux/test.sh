#!/bin/bash
set -e

docker compose -f docker-compose-test.yml build

# Capture and tee output to variable
output=$(docker compose -f docker-compose-test.yml up --abort-on-container-exit 2>&1 | tee /dev/tty)

# Check for failed tests summary line
if echo "$output" | grep -qE "==+ .* failed"; then
  echo "❌ Some test cases failed!"
  exit 1
else
  echo "✅ All tests passed."
fi

docker compose -f docker-compose-test.yml down -v
