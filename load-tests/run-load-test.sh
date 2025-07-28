#!/bin/bash

# Z2 Platform Load Testing Script
# This script provides various load testing scenarios for the Z2 platform

set -e

# Default configuration
HOST="http://localhost:8000"
WEB_PORT="8089"
USERS=10
SPAWN_RATE=2
DURATION="5m"
TEST_TYPE="basic"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --host HOST          Target host (default: http://localhost:8000)"
    echo "  -u, --users USERS        Number of concurrent users (default: 10)"
    echo "  -r, --spawn-rate RATE    User spawn rate per second (default: 2)"
    echo "  -t, --time DURATION      Test duration (default: 5m)"
    echo "  -p, --port PORT          Web UI port (default: 8089)"
    echo "  -T, --test-type TYPE     Test type: basic, stress, burst (default: basic)"
    echo "  --headless               Run without web UI"
    echo "  --csv PREFIX             Save results to CSV files with prefix"
    echo "  --help                   Show this help message"
    echo ""
    echo "Test Types:"
    echo "  basic    - Normal load testing with ApiUser"
    echo "  stress   - High load testing with HighLoadUser"
    echo "  burst    - Burst/spike testing with BurstUser"
    echo ""
    echo "Examples:"
    echo "  $0 --host http://staging.z2.com --users 50 --time 10m"
    echo "  $0 --test-type stress --users 100 --headless --csv results"
    echo "  $0 --test-type burst --users 200 --spawn-rate 10 --time 2m"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -u|--users)
            USERS="$2"
            shift 2
            ;;
        -r|--spawn-rate)
            SPAWN_RATE="$2"
            shift 2
            ;;
        -t|--time)
            DURATION="$2"
            shift 2
            ;;
        -p|--port)
            WEB_PORT="$2"
            shift 2
            ;;
        -T|--test-type)
            TEST_TYPE="$2"
            shift 2
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --csv)
            CSV_PREFIX="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if locust is installed
if ! command -v locust &> /dev/null; then
    print_color $RED "Error: Locust is not installed."
    echo "Install it with: pip install -r requirements.txt"
    exit 1
fi

# Validate test type and set user class
case $TEST_TYPE in
    basic)
        USER_CLASS="ApiUser"
        ;;
    stress)
        USER_CLASS="HighLoadUser"
        ;;
    burst)
        USER_CLASS="BurstUser"
        ;;
    *)
        print_color $RED "Error: Invalid test type '$TEST_TYPE'"
        echo "Valid types: basic, stress, burst"
        exit 1
        ;;
esac

# Build locust command
LOCUST_CMD="locust -f locustfile.py --host $HOST"

if [[ "$HEADLESS" == "true" ]]; then
    LOCUST_CMD="$LOCUST_CMD --headless -u $USERS -r $SPAWN_RATE -t $DURATION"
    if [[ -n "$CSV_PREFIX" ]]; then
        LOCUST_CMD="$LOCUST_CMD --csv $CSV_PREFIX"
    fi
else
    LOCUST_CMD="$LOCUST_CMD --web-port $WEB_PORT"
fi

LOCUST_CMD="$LOCUST_CMD $USER_CLASS"

# Print test configuration
print_color $YELLOW "=== Z2 Platform Load Testing ==="
echo "Host: $HOST"
echo "Test Type: $TEST_TYPE ($USER_CLASS)"
echo "Users: $USERS"
echo "Spawn Rate: $SPAWN_RATE/sec"
echo "Duration: $DURATION"
if [[ "$HEADLESS" != "true" ]]; then
    echo "Web UI: http://localhost:$WEB_PORT"
fi
if [[ -n "$CSV_PREFIX" ]]; then
    echo "CSV Output: ${CSV_PREFIX}_*.csv"
fi
echo ""

# Check if target is reachable
print_color $YELLOW "Checking target connectivity..."
if curl -f -s --max-time 10 "$HOST/health/live" > /dev/null; then
    print_color $GREEN "✓ Target is reachable"
else
    print_color $RED "✗ Target is not reachable at $HOST"
    echo "Make sure the Z2 backend is running and accessible."
    exit 1
fi

# Run the test
print_color $YELLOW "Starting load test..."
echo "Command: $LOCUST_CMD"
echo ""

if [[ "$HEADLESS" == "true" ]]; then
    eval $LOCUST_CMD
    
    # Show results summary if CSV was generated
    if [[ -n "$CSV_PREFIX" && -f "${CSV_PREFIX}_stats.csv" ]]; then
        print_color $GREEN "=== Test Results Summary ==="
        echo "Results saved to ${CSV_PREFIX}_*.csv files"
        
        # Show basic stats
        if command -v python3 &> /dev/null; then
            python3 -c "
import csv
try:
    with open('${CSV_PREFIX}_stats.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Type'] == 'Aggregated':
                print(f'Total Requests: {row[\"Request Count\"]}')
                print(f'Failure Rate: {row[\"Failure Count\"]}')
                print(f'Average Response Time: {row[\"Average Response Time\"]}ms')
                print(f'Max Response Time: {row[\"Max Response Time\"]}ms')
                break
except Exception as e:
    print(f'Could not parse results: {e}')
"
        fi
    fi
else
    print_color $GREEN "Starting Locust web interface..."
    print_color $YELLOW "Open http://localhost:$WEB_PORT in your browser"
    print_color $YELLOW "Press Ctrl+C to stop the test"
    eval $LOCUST_CMD
fi

print_color $GREEN "Load test completed!"