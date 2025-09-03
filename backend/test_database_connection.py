#!/usr/bin/env python3
"""
Test database connection and table existence
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_database():
    """Test database connection and table existence"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Test each table
        tables = ['users', 'user_profiles', 'marketplace_posts', 'user_chats', 'chat_messages']
        
        for table in tables:
            try:
                response = supabase.table(table).select('count').limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' does not exist: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_registration():
    """Test user registration"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Test user data
        user_data = {
            'username': 'Test User',
            'email': 'test@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy',
            'user_type': 'farmer',
            'contact': '1234567890'
        }
        
        try:
            response = supabase.table('users').insert(user_data).execute()
            print("✅ User registration test successful")
            return True
        except Exception as e:
            print(f"❌ User registration failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing FarmLink Database...")
    print("=" * 40)
    
    # Test database connection
    if test_database():
        print("\n🔍 Testing user registration...")
        test_registration()
    else:
        print("\n❌ Database connection failed!")
        print("💡 Please check your .env file and Supabase credentials")
