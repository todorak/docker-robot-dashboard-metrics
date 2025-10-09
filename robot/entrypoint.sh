#!/bin/bash
set -e

echo "=========================================="
echo "Robot Framework Test Runner"
echo "=========================================="
echo "Test Tag: ${1:-All}"
echo "Processes: ${PROCESSES:-6}"
echo "Browser: ${BROWSER:-headlesschrome}"
echo "Output Dir: ${OUTPUT_DIR:-/robot_results}"
echo "=========================================="

# Check if Chrome is available
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "Chrome: $CHROME_VERSION"
fi

# Set default values
TEST_TAG="${1:-}"
OUTPUT_DIR="${OUTPUT_DIR:-/robot_results}"
PROCESSES="${PROCESSES:-6}"

# Clean old results
echo ""
echo "Cleaning old results..."
rm -f ${OUTPUT_DIR}/*.html ${OUTPUT_DIR}/*.xml ${OUTPUT_DIR}/*.log 2>/dev/null || true

# Run tests
echo ""
echo "Starting test execution..."
echo ""

if [ -z "$TEST_TAG" ]; then
    echo "Running ALL tests..."
    python3 /test_runner.py --processes ${PROCESSES}
else
    echo "Running tests with tag: $TEST_TAG"
    python3 /test_runner.py --tag "$TEST_TAG" --processes ${PROCESSES}
fi

EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Test execution completed!"
echo "Exit Code: $EXIT_CODE"
echo "=========================================="
echo ""
echo "Results available in: ${OUTPUT_DIR}"
ls -lh ${OUTPUT_DIR}/*.{html,xml} 2>/dev/null || echo "No result files found"
echo ""

# Keep container running if needed for debugging
if [ "$DEBUG_MODE" = "true" ]; then
    echo "Debug mode enabled - container will stay running"
    tail -f /dev/null
fi

exit $EXIT_CODE
