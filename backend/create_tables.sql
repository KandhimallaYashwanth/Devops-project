-- FarmLink Database Schema
-- Run this SQL in Supabase SQL Editor to create all necessary tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
    contact VARCHAR(15),
    google_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    bio TEXT,
    location VARCHAR(100),
    profile_image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create marketplace_posts table
CREATE TABLE IF NOT EXISTS marketplace_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('farmer', 'buyer')),
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,
    crop_name VARCHAR(100),
    crop_details TEXT,
    quantity VARCHAR(50),
    name VARCHAR(100),
    organization VARCHAR(100),
    requirements TEXT,
    location VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_chats table
CREATE TABLE IF NOT EXISTS user_chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user1_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user2_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID REFERENCES user_chats(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_posts_user_type ON marketplace_posts(user_type);
CREATE INDEX IF NOT EXISTS idx_posts_location ON marketplace_posts(location);
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON chat_messages(chat_id);

-- Insert sample data
INSERT INTO users (username, email, password_hash, user_type, contact) VALUES
('Demo Farmer', 'farmer@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy', 'farmer', '9876543210'),
('Demo Buyer', 'buyer@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s7Hy', 'buyer', '9876543211')
ON CONFLICT (email) DO NOTHING;

-- Insert sample posts
INSERT INTO marketplace_posts (user_type, author_id, crop_name, crop_details, quantity, location) 
SELECT 'farmer', id, 'Organic Tomatoes', 'Fresh organic tomatoes, pesticide-free, harvested yesterday', '50 kg', 'Mumbai, Maharashtra'
FROM users WHERE email = 'farmer@demo.com'
ON CONFLICT DO NOTHING;

INSERT INTO marketplace_posts (user_type, author_id, name, organization, requirements, location)
SELECT 'buyer', id, 'Green Restaurant', 'Restaurant', 'Need fresh vegetables daily for our restaurant kitchen', 'Mumbai, Maharashtra'
FROM users WHERE email = 'buyer@demo.com'
ON CONFLICT DO NOTHING;

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view all users" ON users FOR SELECT USING (true);
CREATE POLICY "Users can insert their own data" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own data" ON users FOR UPDATE USING (true);

CREATE POLICY "Profiles can be viewed by all" ON user_profiles FOR SELECT USING (true);
CREATE POLICY "Users can insert their own profile" ON user_profiles FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own profile" ON user_profiles FOR UPDATE USING (true);

CREATE POLICY "Posts can be viewed by all" ON marketplace_posts FOR SELECT USING (true);
CREATE POLICY "Users can insert their own posts" ON marketplace_posts FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own posts" ON marketplace_posts FOR UPDATE USING (true);

CREATE POLICY "Chats can be viewed by participants" ON user_chats FOR SELECT USING (true);
CREATE POLICY "Users can create chats" ON user_chats FOR INSERT WITH CHECK (true);

CREATE POLICY "Messages can be viewed by chat participants" ON chat_messages FOR SELECT USING (true);
CREATE POLICY "Users can send messages" ON chat_messages FOR INSERT WITH CHECK (true);
