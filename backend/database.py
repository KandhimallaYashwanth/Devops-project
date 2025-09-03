from supabase import create_client, Client
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database initialization and table creation"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Supabase client"""
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None
    
    def create_tables(self) -> bool:
        """Create necessary database tables"""
        if not self.client:
            logger.error("Supabase client not available")
            return False
        
        try:
            # Create users table
            self._create_users_table()
            
            # Create profiles table
            self._create_profiles_table()
            
            # Create posts table
            self._create_posts_table()
            
            # Create chats table
            self._create_chats_table()
            
            # Create messages table
            self._create_messages_table()
            
            logger.info("All tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def _create_users_table(self):
        """Create users table"""
        try:
            # Check if table exists
            result = self.client.table('users').select('id').limit(1).execute()
            logger.info("Users table already exists")
            return
        except Exception:
            logger.info("Creating users table...")
        
        # Create table using SQL (this would typically be done via migrations)
        create_users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(50) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
            contact VARCHAR(15),
            google_id VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
        """
        
        try:
            self.client.rpc('exec_sql', {'sql': create_users_sql}).execute()
            logger.info("Users table created successfully")
        except Exception as e:
            logger.warning(f"Could not create users table via SQL: {e}")
            logger.info("Users table will be created when first data is inserted")
    
    def _create_profiles_table(self):
        """Create user profiles table"""
        try:
            result = self.client.table('user_profiles').select('id').limit(1).execute()
            logger.info("Profiles table already exists")
            return
        except Exception:
            logger.info("Creating profiles table...")
        
        create_profiles_sql = """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255),
            contact VARCHAR(15),
            user_type VARCHAR(20) NOT NULL,
            bio TEXT,
            avatar_url TEXT,
            location VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles(user_id);
        CREATE INDEX IF NOT EXISTS idx_profiles_user_type ON user_profiles(user_type);
        """
        
        try:
            self.client.rpc('exec_sql', {'sql': create_profiles_sql}).execute()
            logger.info("Profiles table created successfully")
        except Exception as e:
            logger.warning(f"Could not create profiles table via SQL: {e}")
    
    def _create_posts_table(self):
        """Create marketplace posts table"""
        try:
            result = self.client.table('marketplace_posts').select('id').limit(1).execute()
            logger.info("Posts table already exists")
            return
        except Exception:
            logger.info("Creating posts table...")
        
        create_posts_sql = """
        CREATE TABLE IF NOT EXISTS marketplace_posts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
            author_id UUID REFERENCES users(id) ON DELETE CASCADE,
            
            -- Farmer post fields
            crop_name VARCHAR(100),
            crop_details TEXT,
            quantity VARCHAR(50),
            
            -- Buyer post fields
            name VARCHAR(100),
            organization VARCHAR(50),
            requirements TEXT,
            
            -- Common fields
            location VARCHAR(255) NOT NULL,
            price DECIMAL(10,2),
            unit VARCHAR(20),
            status VARCHAR(20) DEFAULT 'active',
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_posts_user_type ON marketplace_posts(user_type);
        CREATE INDEX IF NOT EXISTS idx_posts_author_id ON marketplace_posts(author_id);
        CREATE INDEX IF NOT EXISTS idx_posts_location ON marketplace_posts(location);
        CREATE INDEX IF NOT EXISTS idx_posts_created_at ON marketplace_posts(created_at);
        """
        
        try:
            self.client.rpc('exec_sql', {'sql': create_posts_sql}).execute()
            logger.info("Posts table created successfully")
        except Exception as e:
            logger.warning(f"Could not create posts table via SQL: {e}")
    
    def _create_chats_table(self):
        """Create user chats table"""
        try:
            result = self.client.table('user_chats').select('id').limit(1).execute()
            logger.info("Chats table already exists")
            return
        except Exception:
            logger.info("Creating chats table...")
        
        create_chats_sql = """
        CREATE TABLE IF NOT EXISTS user_chats (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user1_id UUID REFERENCES users(id) ON DELETE CASCADE,
            user2_id UUID REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT unique_user_pair UNIQUE(user1_id, user2_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_chats_user1_id ON user_chats(user1_id);
        CREATE INDEX IF NOT EXISTS idx_chats_user2_id ON user_chats(user2_id);
        """
        
        try:
            self.client.rpc('exec_sql', {'sql': create_chats_sql}).execute()
            logger.info("Chats table created successfully")
        except Exception as e:
            logger.warning(f"Could not create chats table via SQL: {e}")
    
    def _create_messages_table(self):
        """Create chat messages table"""
        try:
            result = self.client.table('chat_messages').select('id').limit(1).execute()
            logger.info("Messages table already exists")
            return
        except Exception:
            logger.info("Creating messages table...")
        
        create_messages_sql = """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            chat_id UUID REFERENCES user_chats(id) ON DELETE CASCADE,
            sender_id UUID REFERENCES users(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            message_type VARCHAR(20) DEFAULT 'text',
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON chat_messages(chat_id);
        CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON chat_messages(sender_id);
        CREATE INDEX IF NOT EXISTS idx_messages_created_at ON chat_messages(created_at);
        """
        
        try:
            self.client.rpc('exec_sql', {'sql': create_messages_sql}).execute()
            logger.info("Messages table created successfully")
        except Exception as e:
            logger.warning(f"Could not create messages table via SQL: {e}")
    
    def insert_sample_data(self) -> bool:
        """Insert sample data for testing"""
        if not self.client:
            logger.error("Supabase client not available")
            return False
        
        try:
            # Insert sample users
            self._insert_sample_users()
            
            # Insert sample posts
            self._insert_sample_posts()
            
            logger.info("Sample data inserted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting sample data: {e}")
            return False
    
    def _insert_sample_users(self):
        """Insert sample users"""
        sample_users = [
            {
                'username': 'farmer_john',
                'email': 'john@farm.com',
                'password_hash': 'hashed_password_here',
                'user_type': 'farmer',
                'contact': '9876543210'
            },
            {
                'username': 'restaurant_owner',
                'email': 'owner@restaurant.com',
                'password_hash': 'hashed_password_here',
                'user_type': 'buyer',
                'contact': '9876543211'
            }
        ]
        
        for user_data in sample_users:
            try:
                self.client.table('users').insert(user_data).execute()
                logger.info(f"Sample user created: {user_data['username']}")
            except Exception as e:
                logger.warning(f"Could not create sample user {user_data['username']}: {e}")
    
    def _insert_sample_posts(self):
        """Insert sample marketplace posts"""
        sample_posts = [
            {
                'user_type': 'farmer',
                'author_id': 'sample_farmer_id',
                'crop_name': 'Organic Tomatoes',
                'crop_details': 'Fresh organic tomatoes, pesticide-free, harvested yesterday',
                'quantity': '50 kg',
                'location': 'Mumbai, Maharashtra',
                'price': 80.00,
                'unit': 'kg'
            },
            {
                'user_type': 'buyer',
                'author_id': 'sample_buyer_id',
                'name': 'Green Restaurant',
                'organization': 'Restaurant',
                'requirements': 'Need fresh vegetables daily for our restaurant kitchen',
                'location': 'Mumbai, Maharashtra',
                'price': 100.00,
                'unit': 'kg'
            }
        ]
        
        for post_data in sample_posts:
            try:
                self.client.table('marketplace_posts').insert(post_data).execute()
                logger.info(f"Sample post created: {post_data.get('crop_name', post_data.get('name'))}")
            except Exception as e:
                logger.warning(f"Could not create sample post: {e}")
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about database tables"""
        if not self.client:
            return {'error': 'Database client not available'}
        
        tables = ['users', 'user_profiles', 'marketplace_posts', 'user_chats', 'chat_messages']
        table_info = {}
        
        for table in tables:
            try:
                result = self.client.table(table).select('*').limit(1).execute()
                table_info[table] = {
                    'exists': True,
                    'count': len(result.data) if result.data else 0
                }
            except Exception as e:
                table_info[table] = {
                    'exists': False,
                    'error': str(e)
                }
        
        return table_info
    
    def reset_database(self) -> bool:
        """Reset database (drop all tables) - USE WITH CAUTION"""
        if not self.client:
            logger.error("Supabase client not available")
            return False
        
        try:
            tables = ['chat_messages', 'user_chats', 'marketplace_posts', 'user_profiles', 'users']
            
            for table in tables:
                try:
                    self.client.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                    logger.info(f"Cleared table: {table}")
                except Exception as e:
                    logger.warning(f"Could not clear table {table}: {e}")
            
            logger.info("Database reset completed")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False

def initialize_database(supabase_url: str, supabase_key: str, insert_samples: bool = False) -> DatabaseManager:
    """Initialize database and return manager instance"""
    db_manager = DatabaseManager(supabase_url, supabase_key)
    
    if db_manager.client:
        # Create tables
        db_manager.create_tables()
        
        # Optionally insert sample data
        if insert_samples:
            db_manager.insert_sample_data()
    
    return db_manager

if __name__ == "__main__":
    # This can be run directly to initialize the database
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        db_manager = initialize_database(supabase_url, supabase_key, insert_samples=True)
        
        # Print table information
        table_info = db_manager.get_table_info()
        print("Database Status:")
        for table, info in table_info.items():
            print(f"  {table}: {'✓' if info.get('exists') else '✗'}")
    else:
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")

