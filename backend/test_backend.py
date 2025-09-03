#!/usr/bin/env python3
"""
Test FarmLink Backend Endpoints
"""

import requests
import json

def test_backend_health():
    """Test if backend is running and accessible"""
    try:
        response = requests.get('http://localhost:5000/')
        print(f"✅ Backend is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_registration_endpoint():
    """Test the registration endpoint"""
    try:
        test_user = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "testpassword123",
            "user_type": "farmer",
            "contact": "9876543211"
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/register',
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📝 Registration endpoint test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Registration successful!")
            data = response.json()
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            return True
        elif response.status_code == 500:
            print("   ❌ Internal Server Error")
            print(f"   Response: {response.text}")
            return False
        elif response.status_code == 409:
            print("   ⚠️ User already exists (this is expected for duplicate emails)")
            print("   Response: {response.text}")
            return True  # This is actually a success case
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
        return False

def test_login_endpoint():
    """Test the login endpoint"""
    try:
        test_credentials = {
            "email": "test2@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=test_credentials,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"🔐 Login endpoint test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            data = response.json()
            print(f"   Token: {data.get('token', 'N/A')[:20]}...")
            return True
        elif response.status_code == 500:
            print("   ❌ Internal Server Error")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

def test_google_oauth_endpoint():
    """Test the Google OAuth URL endpoint"""
    try:
        test_data = {
            "user_type": "farmer"
        }
        
        response = requests.post(
            'http://localhost:5000/api/auth/google/url',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"🔑 Google OAuth endpoint test:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ OAuth URL generated successfully!")
            data = response.json()
            print(f"   Auth URL: {data.get('auth_url', 'N/A')[:50]}...")
            return True
        elif response.status_code == 500:
            print("   ❌ Internal Server Error")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google OAuth: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing FarmLink Backend...")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not accessible. Please start it first.")
        exit(1)
    
    print("\n🔍 Testing Endpoints...")
    
    # Test registration
    registration_ok = test_registration_endpoint()
    
    # Test login (only if registration was successful)
    if registration_ok:
        test_login_endpoint()
    
    # Test Google OAuth
    test_google_oauth_endpoint()
    
    print("\n🎯 Test Complete!")
    if not registration_ok:
        print("💡 Registration failed - this is likely the source of your 500 error")
        print("💡 Check your backend logs for more details")
