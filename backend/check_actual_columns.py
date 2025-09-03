#!/usr/bin/env python3
"""
Check what columns actually exist in the users table
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_column_combinations():
    """Test different column combinations to find what exists"""
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Connected to Supabase")
        
        # Test different column combinations
        test_cases = [
            {'email': 'test@test.com', 'password_hash': 'hash'},
            {'email': 'test@test.com', 'password_hash': 'hash', 'name': 'Test'},
            {'email': 'test@test.com', 'password_hash': 'hash', 'name': 'Test', 'user_type': 'farmer'},
            {'email': 'test@test.com', 'password_hash': 'hash', 'name': 'Test', 'user_type': 'farmer', 'contact': '123'},
        ]
        
        for i, test_data in enumerate(test_cases):
            try:
                print(f"\n🔍 Test {i+1}: {list(test_data.keys())}")
                response = supabase.table('users').insert(test_data).execute()
                print(f"✅ Success! These columns exist: {list(test_data.keys())}")
                
                # Clean up
                supabase.table('users').delete().eq('email', 'test@test.com').execute()
                return test_data.keys()
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                if "Could not find" in str(e):
                    # Extract the column name from the error
                    error_msg = str(e)
                    if "column" in error_msg:
                        print(f"💡 Missing column detected in error message")
        
        return None
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Checking Actual Table Structure...")
    print("=" * 50)
    
    existing_columns = test_column_combinations()
    
    if existing_columns:
        print(f"\n✅ Found existing columns: {list(existing_columns)}")
        print("\n💡 Your table structure is different from what the backend expects.")
        print("💡 You need to either:")
        print("   1. Add missing columns to your table, OR")
        print("   2. Update the backend code to match your table structure")
    else:
        print("\n❌ Could not determine table structure")
        print("💡 Please check your Supabase table manually")
