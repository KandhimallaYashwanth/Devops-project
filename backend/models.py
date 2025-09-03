from datetime import datetime
import uuid
from typing import Dict, List, Optional, Any
from supabase import Client

class User:
    """User model for authentication and profile management"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = 'users'
    
    def create(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            user_data['id'] = str(uuid.uuid4())
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table(self.table_name).insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table(self.table_name).update(update_data).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

class Profile:
    """User profile model"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = 'user_profiles'
    
    def create(self, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user profile"""
        try:
            profile_data['created_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table(self.table_name).insert(profile_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating profile: {e}")
            return None
    
    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get profile by user ID"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def update(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table(self.table_name).update(update_data).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating profile: {e}")
            return None

class Post:
    """Marketplace post model"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = 'marketplace_posts'
    
    def create(self, post_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new marketplace post"""
        try:
            post_data['id'] = str(uuid.uuid4())
            post_data['created_at'] = datetime.utcnow().isoformat()
            post_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table(self.table_name).insert(post_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
    
    # Find this function in models.py (around line 111-129)
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table(self.table_name).select('*').order('created_at', desc=True)
            
            if filters:
                if filters.get('user_type'):
                    query = query.eq('user_type', filters['user_type'])
                if filters.get('location'):
                    query = query.ilike('location', f"%{filters['location']}%")
                if filters.get('search'):
                    search_term = filters['search']
                    # Modified this line to fix the search
                    query = query.ilike('crop_name', f"%{search_term}%")
        
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get posts by a specific user"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('author_id', user_id).order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user posts: {e}")
            return []
    
    def get_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get post by ID"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('id', post_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting post by ID: {e}")
            return None
    
    def update(self, post_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a post"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table(self.table_name).update(update_data).eq('id', post_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating post: {e}")
            return None
    
    def delete(self, post_id: str) -> bool:
        """Delete a post"""
        try:
            result = self.supabase.table(self.table_name).delete().eq('id', post_id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"Error deleting post: {e}")
            return False

class Chat:
    """Chat model for user conversations"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = 'user_chats'
    
    def create(self, user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
        """Create a new chat between two users"""
        try:
            chat_data = {
                'id': str(uuid.uuid4()),
                'user1_id': user1_id,
                'user2_id': user2_id,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table(self.table_name).insert(chat_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating chat: {e}")
            return None
    
    def get_by_users(self, user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
        """Get chat between two specific users"""
        try:
            result = self.supabase.table(self.table_name).select('*').or_(f"user1_id.eq.{user1_id}.and.user2_id.eq.{user2_id},user1_id.eq.{user2_id}.and.user2_id.eq.{user1_id}").execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting chat by users: {e}")
            return None
    
    def get_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chats for a specific user"""
        try:
            result = self.supabase.table(self.table_name).select('*').or_(f"user1_id.eq.{user_id},user2_id.eq.{user_id}").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting user chats: {e}")
            return []

class Message:
    """Chat message model"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table_name = 'chat_messages'
    
    def create(self, chat_id: str, sender_id: str, message_text: str) -> Optional[Dict[str, Any]]:
        """Create a new chat message"""
        try:
            message_data = {
                'id': str(uuid.uuid4()),
                'chat_id': chat_id,
                'sender_id': sender_id,
                'message': message_text,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table(self.table_name).insert(message_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific chat"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('chat_id', chat_id).order('created_at', asc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []
    
    def get_last_message(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get the last message in a chat"""
        try:
            result = self.supabase.table(self.table_name).select('*').eq('chat_id', chat_id).order('created_at', desc=True).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting last message: {e}")
            return None

