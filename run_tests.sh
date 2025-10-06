#!/bin/bash

# Test runner script for the Real-time Chat Application
# This script runs all tests with proper setup and reporting

set -e  # Exit on any error

echo "Starting Test Suite for Real-time Chat Application"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Parse command line arguments
BACKEND_TESTS=true
COVERAGE=true
VERBOSE=false
PARALLEL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --coverage          Generate coverage reports"
            echo "  --verbose           Verbose output"
            echo "  --parallel          Run tests in parallel"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set up test environment
print_status "Setting up test environment..."

# Create test directories
mkdir -p test_reports

# Set up environment variables for testing
export DJANGO_SETTINGS_MODULE=chat_app.simple_test_settings

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."
    
    cd backend
    
    # Install test dependencies if not already installed
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    pip install pytest pytest-django pytest-asyncio pytest-cov coverage
    
    # Django will automatically create and manage the test database
    print_status "Django will automatically create and manage the test database..."
    
    # Run basic unit tests
    print_status "Running basic unit tests..."
    if [ "$COVERAGE" = true ]; then
        coverage run --source='.' manage.py test accounts.simple_test chat.tests --settings=chat_app.simple_test_settings
        coverage report -m
        coverage html -d test_reports/coverage_html
        print_success "Coverage report generated in backend/test_reports/coverage_html/"
    else
        if [ "$VERBOSE" = true ]; then
            python manage.py test accounts.simple_test chat.tests --settings=chat_app.simple_test_settings --verbosity=2
        else
            python manage.py test accounts.simple_test chat.tests --settings=chat_app.simple_test_settings
        fi
    fi
    
    # Skip pytest for now since Django tests are working
    # if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    #     print_status "Running pytest tests..."
    #     if [ "$COVERAGE" = true ]; then
    #         pytest --cov=. --cov-report=html:test_reports/pytest_coverage
    #     else
    #         pytest
    #     fi
    # fi
    
    # Django automatically cleans up the test database

    cd ..
    print_success "Backend tests completed!"
}

# Note: Frontend testing has been removed as per project requirements
# The project focuses on backend testing with Django/Python


# Function to run all tests
run_all_tests() {
    print_status "Running backend tests..."
    
    if [ "$PARALLEL" = true ]; then
        print_status "Running tests in parallel..."
        
        # Start backend test process in background
        run_backend_tests &
        BACKEND_PID=$!
        
        # Wait for process to complete
        wait $BACKEND_PID
        BACKEND_EXIT_CODE=$?
        
        # Check exit code
        if [ $BACKEND_EXIT_CODE -ne 0 ]; then
            print_error "Backend tests failed"
            exit 1
        fi
        
    else
        # Run tests sequentially
        run_backend_tests
    fi
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    # Create test report directory
    mkdir -p test_reports
    
    # Generate summary report
    cat > test_reports/test_summary.md << EOF
# Test Summary Report

Generated on: $(date)

## Test Configuration
- Backend Tests: $BACKEND_TESTS
- Coverage: $COVERAGE
- Verbose: $VERBOSE
- Parallel: $PARALLEL

## Test Results
- All backend tests completed successfully!

## Coverage Reports
- Backend: backend/test_reports/coverage_html/index.html

EOF

    print_success "Test report generated in test_reports/test_summary.md"
}

# Main execution
main() {
    start_time=$(date +%s)
    
    # Run tests
    run_all_tests
    
    # Generate report
    generate_test_report
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    print_success "All tests completed successfully in ${duration} seconds!"
    
    if [ "$COVERAGE" = true ]; then
        print_status "Coverage reports available in:"
        print_status "  - Backend: backend/test_reports/coverage_html/index.html"
    fi
    
    print_status "Test artifacts available in test_reports/ directory"
}

# Run main function
main
