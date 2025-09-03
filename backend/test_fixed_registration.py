#!/usr/bin/env python3
"""
Test registration with corrected table structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_registration():
    """Test user registration with correct column names"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Test user data with correct column names
        user_data = {
            'name': 'Test User',
            'email': 'test2@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy',
            'user_type': 'farmer',
            'mobile': '9876543210'
        }
        
        print("🔍 Testing registration with corrected column names...")
        response = supabase.table('users').insert(user_data).execute()
        print("✅ User registration successful!")
        
        # Get the created user
        user = response.data[0]
        print(f"✅ Created user: {user['name']} ({user['email']})")
        
        # Clean up
        supabase.table('users').delete().eq('email', 'test2@example.com').execute()
        print("✅ Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Fixed Registration...")
    print("=" * 40)
    
    if test_registration():
        print("\n🎉 Registration works correctly!")
        print("💡 You need to restart your backend server to apply the changes")
        print("💡 Run: python app.py")
    else:
        print("\n❌ Registration still has issues")
        print("💡 Check your table structure in Supabase")
