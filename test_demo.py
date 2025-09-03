import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print("✅ Health Check:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        print()
        return False

def test_demo_setup():
    """Test the demo setup endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/api/demo/setup")
        print("✅ Demo Setup:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        return True
    except Exception as e:
        print(f"❌ Demo Setup Failed: {e}")
        print()
        return False

def test_login():
    """Test login with demo credentials"""
    try:
        login_data = {
            "email": "farmer@demo.com",
            "password": "demo123"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print("✅ Login Test:")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        if response.status_code == 200:
            print(f"Token: {result.get('token', 'No token')}")
        print()
        return result.get('token') if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        print()
        return None

def test_posts():
    """Test getting posts"""
    try:
        response = requests.get(f"{BASE_URL}/api/posts")
        print("✅ Get Posts:")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Posts Count: {result.get('count', 0)}")
        if result.get('posts'):
            for post in result['posts'][:2]:  # Show first 2 posts
                print(f"  - {post.get('crop_name', post.get('name', 'Unknown'))} in {post.get('location', 'Unknown')}")
        print()
        return True
    except Exception as e:
        print(f"❌ Get Posts Failed: {e}")
        print()
        return False

def test_create_post(token):
    """Test creating a post (requires authentication)"""
    if not token:
        print("❌ Cannot test create post - no token available")
        print()
        return False
    
    try:
        post_data = {
            "crop_name": "Test Carrots",
            "crop_details": "Fresh organic carrots for testing",
            "quantity": "25 kg",
            "location": "Test Location"
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.post(
            f"{BASE_URL}/api/posts",
            json=post_data,
            headers=headers
        )
        print("✅ Create Post:")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        print()
        return True
    except Exception as e:
        print(f"❌ Create Post Failed: {e}")
        print()
        return False

def main():
    """Run all tests"""
    print("🚀 FarmLink API Testing")
    print("=" * 50)
    print()
    
    # Test health endpoint
    if not test_health():
        print("❌ Backend is not running or not accessible")
        print("Make sure you have 'python app_simple.py' running in another terminal")
        return
    
    # Test demo setup
    test_demo_setup()
    
    # Test login
    token = test_login()
    
    # Test getting posts
    test_posts()
    
    # Test creating a post (if we have a token)
    if token:
        test_create_post(token)
    
    print("🎯 Testing Complete!")
    print("If all tests passed, your backend is working perfectly!")

if __name__ == "__main__":
    main()
