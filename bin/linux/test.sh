#!/bin/bash
set -e

docker compose -f docker-compose-test.yml build

TEMP_LOG_FILE=$(mktemp)

docker compose -f docker-compose-test.yml up --abort-on-container-exit 2>&1 | tee "$TEMP_LOG_FILE"

if grep -qE "==+ .* failed" "$TEMP_LOG_FILE"; then
  echo "❌ Some test cases failed!"
  exit 1
else
  echo "✅ All tests passed."
fi

docker compose -f docker-compose-test.yml down -v
