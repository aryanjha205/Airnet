CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS users(id UUID PRIMARY KEY DEFAULT gen_random_uuid(),username VARCHAR(50) UNIQUE NOT NULL,email VARCHAR(255) UNIQUE NOT NULL,password_hash TEXT NOT NULL,avatar_url TEXT,created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS rooms(id UUID PRIMARY KEY DEFAULT gen_random_uuid(),name VARCHAR(100) NOT NULL,is_private BOOLEAN DEFAULT false,created_by UUID REFERENCES users(id),created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS room_members(room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,user_id UUID REFERENCES users(id) ON DELETE CASCADE,joined_at TIMESTAMPTZ DEFAULT now(),role VARCHAR(20) DEFAULT 'member',PRIMARY KEY(room_id,user_id));
CREATE TABLE IF NOT EXISTS messages(id UUID PRIMARY KEY DEFAULT gen_random_uuid(),room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,user_id UUID REFERENCES users(id) ON DELETE CASCADE,content TEXT NOT NULL,created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS presence(user_id UUID REFERENCES users(id) ON DELETE CASCADE,room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,status VARCHAR(20) DEFAULT 'online',updated_at TIMESTAMPTZ DEFAULT now(),PRIMARY KEY(user_id,room_id));
CREATE INDEX IF NOT EXISTS idx_messages_room_created ON messages(room_id,created_at DESC);
CREATE INDEX IF NOT EXISTS idx_room_members_user ON room_members(user_id);
