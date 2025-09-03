#!/usr/bin/env python3
"""
FarmLink Backend API Test Script
Test the main API endpoints to ensure they're working correctly
"""

import requests
import json
import sys
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5000/api"

def print_test_result(test_name, success, message=""):
    """Print test result with formatting"""
    if success:
        print(f"✅ {test_name}: PASSED")
    else:
        print(f"❌ {test_name}: FAILED - {message}")
    return success

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            return print_test_result("Health Check", True, f"Status: {data.get('status')}")
        else:
            return print_test_result("Health Check", False, f"Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        return print_test_result("Health Check", False, "Server not running")
    except Exception as e:
        return print_test_result("Health Check", False, str(e))

def test_registration():
    """Test user registration"""
    try:
        user_data = {
            "username": "test_farmer",
            "email": f"test_farmer_{datetime.now().timestamp()}@test.com",
            "password": "testpassword123",
            "user_type": "farmer",
            "contact": "9876543210"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        if response.status_code == 201:
            data = response.json()
            if 'token' in data and 'user' in data:
                return print_test_result("User Registration", True, f"User ID: {data['user']['id']}")
            else:
                return print_test_result("User Registration", False, "Missing token or user data")
        else:
            return print_test_result("User Registration", False, f"Status code: {response.status_code}")
    except Exception as e:
        return print_test_result("User Registration", False, str(e))

def test_login():
    """Test user login"""
    try:
        login_data = {
            "email": "test_farmer@test.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                return print_test_result("User Login", True, "Login successful")
            else:
                return print_test_result("User Login", False, "Missing token")
        else:
            return print_test_result("User Login", False, f"Status code: {response.status_code}")
    except Exception as e:
        return print_test_result("User Login", False, str(e))

def test_posts_endpoint():
    """Test the posts endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/posts")
        
        if response.status_code == 200:
            data = response.json()
            return print_test_result("Get Posts", True, f"Found {data.get('count', 0)} posts")
        else:
            return print_test_result("Get Posts", False, f"Status code: {response.status_code}")
    except Exception as e:
        return print_test_result("Get Posts", False, str(e))

def test_unauthorized_access():
    """Test that protected endpoints require authentication"""
    try:
        response = requests.get(f"{BASE_URL}/profile")
        
        if response.status_code == 401:
            return print_test_result("Unauthorized Access", True, "Correctly blocked unauthorized access")
        else:
            return print_test_result("Unauthorized Access", False, f"Expected 401, got {response.status_code}")
    except Exception as e:
        return print_test_result("Unauthorized Access", False, str(e))

def run_all_tests():
    """Run all API tests"""
    print("🧪 Starting FarmLink Backend API Tests")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_registration,
        test_login,
        test_posts_endpoint,
        test_unauthorized_access
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        sys.exit(1)









