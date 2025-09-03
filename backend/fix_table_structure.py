#!/usr/bin/env python3
"""
Fix table structure to match backend expectations
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def fix_users_table():
    """Add missing columns to users table"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Try to insert a test user with minimal data first
        test_user = {
            'username': 'Test User',
            'email': 'test@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy',
            'user_type': 'farmer'
        }
        
        print("🔍 Testing user insertion with minimal data...")
        try:
            response = supabase.table('users').insert(test_user).execute()
            print("✅ User inserted successfully with minimal data")
            
            # Now try with contact field
            test_user_with_contact = {
                'username': 'Test User 2',
                'email': 'test2@example.com',
                'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy',
                'user_type': 'farmer',
                'contact': '1234567890'
            }
            
            print("🔍 Testing user insertion with contact field...")
            response = supabase.table('users').insert(test_user_with_contact).execute()
            print("✅ User inserted successfully with contact field")
            
        except Exception as e:
            print(f"❌ Error inserting user: {e}")
            
            # If contact field doesn't exist, we need to add it
            if "contact" in str(e):
                print("🔧 Contact column missing. You need to add it to your users table.")
                print("💡 Go to Supabase Dashboard → Table Editor → users table")
                print("💡 Add column: contact (varchar(15))")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_required_columns():
    """Check what columns are missing"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Try to get the table structure by attempting different field combinations
        test_cases = [
            {'username': 'test', 'email': 'test@test.com', 'password_hash': 'hash', 'user_type': 'farmer'},
            {'username': 'test', 'email': 'test@test.com', 'password_hash': 'hash', 'user_type': 'farmer', 'contact': '123'},
            {'username': 'test', 'email': 'test@test.com', 'password_hash': 'hash', 'user_type': 'farmer', 'contact': '123', 'created_at': '2023-01-01'},
            {'username': 'test', 'email': 'test@test.com', 'password_hash': 'hash', 'user_type': 'farmer', 'contact': '123', 'created_at': '2023-01-01', 'updated_at': '2023-01-01'}
        ]
        
        for i, test_data in enumerate(test_cases):
            try:
                response = supabase.table('users').insert(test_data).execute()
                print(f"✅ Test case {i+1} successful: {list(test_data.keys())}")
                # Clean up
                supabase.table('users').delete().eq('email', 'test@test.com').execute()
            except Exception as e:
                print(f"❌ Test case {i+1} failed: {e}")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Fixing FarmLink Database Structure...")
    print("=" * 50)
    
    if not fix_users_table():
        print("\n📋 Manual Fix Required:")
        print("1. Go to Supabase Dashboard")
        print("2. Navigate to Table Editor")
        print("3. Click on 'users' table")
        print("4. Add these missing columns:")
        print("   - contact: varchar(15)")
        print("   - created_at: timestamptz (Default: now())")
        print("   - updated_at: timestamptz (Default: now())")
        print("5. Run this script again")
    else:
        print("\n✅ Table structure is correct!")
        print("🚀 You can now use your FarmLink application!")
