#!/usr/bin/env python3
"""
Test Google OAuth integration for FarmLink
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_oauth_config():
    """Test if Google OAuth is properly configured"""
    
    print("🔍 Testing Google OAuth Configuration...")
    print("=" * 50)
    
    # Check environment variables
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    google_redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/auth/google/callback')
    
    print(f"✅ GOOGLE_CLIENT_ID: {'SET' if google_client_id else 'NOT SET'}")
    print(f"✅ GOOGLE_CLIENT_SECRET: {'SET' if google_client_secret else 'NOT SET'}")
    print(f"✅ GOOGLE_REDIRECT_URI: {google_redirect_uri}")
    
    if not google_client_id or not google_client_secret:
        print("\n❌ Google OAuth not configured!")
        print("💡 Add these to your .env file:")
        print("   GOOGLE_CLIENT_ID=your-google-client-id")
        print("   GOOGLE_CLIENT_SECRET=your-google-client-secret")
        print("\n🔗 Get credentials from: https://console.cloud.google.com/")
        return False
    
    print("\n✅ Google OAuth is properly configured!")
    return True

def test_oauth_endpoints():
    """Test if OAuth endpoints are accessible"""
    
    print("\n🔍 Testing OAuth Endpoints...")
    print("=" * 50)
    
    import requests
    
    try:
        # Test the OAuth URL endpoint
        response = requests.post('http://localhost:5000/api/auth/google/url', 
                               json={'user_type': 'farmer'})
        
        if response.status_code == 200:
            print("✅ /api/auth/google/url endpoint working")
            data = response.json()
            if 'auth_url' in data:
                print(f"✅ Generated auth URL: {data['auth_url'][:50]}...")
            else:
                print("❌ No auth_url in response")
        else:
            print(f"❌ /api/auth/google/url endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running")
        print("💡 Start your backend with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error testing OAuth endpoints: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing FarmLink Google OAuth Integration...")
    print("=" * 60)
    
    # Test configuration
    if test_google_oauth_config():
        # Test endpoints
        test_oauth_endpoints()
    
    print("\n🎯 Next Steps:")
    print("1. Get Google OAuth credentials from Google Cloud Console")
    print("2. Add them to your .env file")
    print("3. Restart your backend: python app.py")
    print("4. Test Google OAuth in your frontend")
