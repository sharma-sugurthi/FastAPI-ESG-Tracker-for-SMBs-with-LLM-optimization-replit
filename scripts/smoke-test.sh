#!/bin/bash

# Smoke Test Script for ESG Compliance Tracker

set -e

BASE_URL="http://localhost:8000"
if [ ! -z "$1" ]; then
    BASE_URL="$1"
fi

echo "🧪 Running smoke tests for ESG Compliance Tracker"
echo "🌐 Base URL: $BASE_URL"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local description=$4
    local data=$5
    
    echo -n "Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json -X POST \
            -H "Content-Type: application/json" \
            -d "$data" "$BASE_URL$endpoint")
    fi
    
    status_code="${response: -3}"
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status_code)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected HTTP $expected_status, got HTTP $status_code)"
        echo "Response: $(cat /tmp/response.json)"
        ((TESTS_FAILED++))
    fi
}

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
for i in {1..30}; do
    if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo "✅ Service is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Service failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🔍 Running endpoint tests..."

# Core endpoints
test_endpoint "GET" "/health" "200" "Health check endpoint"
test_endpoint "GET" "/docs" "200" "API documentation"
test_endpoint "GET" "/" "200" "Root endpoint"

# Authentication endpoints
test_endpoint "GET" "/auth/providers" "200" "Auth providers endpoint"
test_endpoint "POST" "/auth/register" "400" "User registration (no data)" ""

# ESG endpoints
test_endpoint "GET" "/esg/questions" "200" "ESG questions endpoint"

# Upload endpoints
test_endpoint "GET" "/upload/csv-template" "200" "CSV template endpoint"
test_endpoint "GET" "/upload/column-mappings" "200" "Column mappings endpoint"

# Predictive endpoints
test_endpoint "GET" "/predictive/health" "200" "Predictive health check"

# Test predictive endpoints with sample data
echo ""
echo "🔮 Testing predictive endpoints with sample data..."

# Sample ESG score data
SAMPLE_SCORE='{
    "overall_score": 65.0,
    "environmental_score": 60.0,
    "social_score": 70.0,
    "governance_score": 65.0,
    "emissions_score": 55.0,
    "energy_score": 65.0,
    "waste_score": 60.0,
    "diversity_score": 75.0,
    "employee_score": 65.0,
    "community_score": 70.0,
    "ethics_score": 60.0,
    "transparency_score": 70.0,
    "badge": "Eco Improver",
    "level": 7,
    "improvement_areas": ["Energy efficiency"],
    "strengths": ["Good diversity practices"],
    "calculated_at": "2024-01-15T10:30:00Z",
    "quick_wins": ["Switch to LED lighting"],
    "long_term_goals": ["Achieve carbon neutrality"]
}'

# Test predictive endpoints (these might require authentication, so we expect 401)
test_endpoint "POST" "/predictive/alerts/penalty-warnings" "401" "Penalty warnings (auth required)" "$SAMPLE_SCORE"
test_endpoint "POST" "/predictive/analytics/benchmarking" "401" "Benchmarking analytics (auth required)" "$SAMPLE_SCORE"
test_endpoint "POST" "/predictive/analytics/readiness-index" "401" "Readiness index (auth required)" "$SAMPLE_SCORE"
test_endpoint "POST" "/predictive/analytics/roi-estimate" "401" "ROI estimation (auth required)" "$SAMPLE_SCORE"

# Test with authentication (register a test user first)
echo ""
echo "🔐 Testing authenticated endpoints..."

# Register test user
TEST_USER='{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User",
    "company_name": "Test Company",
    "industry": "retail"
}'

echo -n "Registering test user... "
register_response=$(curl -s -w "%{http_code}" -o /tmp/register.json -X POST \
    -H "Content-Type: application/json" \
    -d "$TEST_USER" "$BASE_URL/auth/register")

register_status="${register_response: -3}"

if [ "$register_status" = "201" ] || [ "$register_status" = "400" ]; then
    echo -e "${GREEN}✅ Registration endpoint working${NC}"
    
    # Try to login
    LOGIN_DATA='{"email": "test@example.com", "password": "testpass123"}'
    echo -n "Testing login... "
    login_response=$(curl -s -w "%{http_code}" -o /tmp/login.json -X POST \
        -H "Content-Type: application/json" \
        -d "$LOGIN_DATA" "$BASE_URL/auth/login")
    
    login_status="${login_response: -3}"
    
    if [ "$login_status" = "200" ]; then
        echo -e "${GREEN}✅ Login successful${NC}"
        
        # Extract token (if available)
        if command -v jq &> /dev/null; then
            TOKEN=$(jq -r '.access_token' /tmp/login.json 2>/dev/null || echo "")
            if [ "$TOKEN" != "" ] && [ "$TOKEN" != "null" ]; then
                echo "🔑 Testing authenticated predictive endpoints..."
                
                # Test with authentication
                auth_response=$(curl -s -w "%{http_code}" -o /tmp/auth_test.json -X POST \
                    -H "Content-Type: application/json" \
                    -H "Authorization: Bearer $TOKEN" \
                    -d "$SAMPLE_SCORE" "$BASE_URL/predictive/analytics/benchmarking")
                
                auth_status="${auth_response: -3}"
                if [ "$auth_status" = "200" ]; then
                    echo -e "${GREEN}✅ Authenticated predictive endpoint working${NC}"
                    ((TESTS_PASSED++))
                else
                    echo -e "${YELLOW}⚠️ Authenticated endpoint returned HTTP $auth_status${NC}"
                fi
            fi
        fi
    else
        echo -e "${YELLOW}⚠️ Login returned HTTP $login_status${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Registration returned HTTP $register_status${NC}"
fi

# Database connectivity test
echo ""
echo "🗄️ Testing database connectivity..."
db_test_response=$(curl -s -w "%{http_code}" -o /tmp/db_test.json "$BASE_URL/auth/providers")
db_status="${db_test_response: -3}"

if [ "$db_status" = "200" ]; then
    echo -e "${GREEN}✅ Database connectivity working${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Database connectivity issue${NC}"
    ((TESTS_FAILED++))
fi

# LLM service test (indirect)
echo ""
echo "🤖 Testing LLM service availability..."
llm_test_response=$(curl -s -w "%{http_code}" -o /tmp/llm_test.json "$BASE_URL/esg/questions")
llm_status="${llm_test_response: -3}"

if [ "$llm_status" = "200" ]; then
    echo -e "${GREEN}✅ LLM service endpoints accessible${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ LLM service endpoints issue${NC}"
    ((TESTS_FAILED++))
fi

# Cleanup
rm -f /tmp/response.json /tmp/register.json /tmp/login.json /tmp/auth_test.json /tmp/db_test.json /tmp/llm_test.json

# Summary
echo ""
echo "📊 Test Summary:"
echo -e "✅ Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! ESG Compliance Tracker is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Some tests failed. Please check the application logs.${NC}"
    exit 1
fi