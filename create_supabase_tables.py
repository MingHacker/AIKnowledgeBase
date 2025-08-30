#!/usr/bin/env python3
"""
在Supabase中创建必要表的脚本
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
load_dotenv()

def create_tables():
    """在Supabase中创建必要的表"""
    try:
        # 获取Supabase配置
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ 环境变量未正确加载")
            return False
            
        print(f"连接到Supabase: {supabase_url}")
        supabase = create_client(supabase_url, supabase_key)
        
        # 创建user_profiles表
        print("创建user_profiles表...")
        try:
            # 检查表是否存在
            result = supabase.table("user_profiles").select("*").limit(1).execute()
            print("✅ user_profiles表已存在")
        except Exception as e:
            if "table" in str(e).lower() and "not found" in str(e).lower():
                print("创建user_profiles表...")
                # 这里需要手动在Supabase SQL编辑器中运行SQL
                print("请在Supabase SQL编辑器中运行以下SQL:")
                print("""
                CREATE TABLE user_profiles (
                    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
                    username VARCHAR(100) UNIQUE,
                    full_name VARCHAR(255),
                    bio TEXT,
                    avatar_url VARCHAR(500),
                    preferences JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE INDEX idx_user_profiles_username ON user_profiles(username);
                
                ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
                
                CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
                CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
                CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
                """)
            else:
                print(f"检查user_profiles表时出错: {e}")
        
        # 创建user_settings表
        print("创建user_settings表...")
        try:
            result = supabase.table("user_settings").select("*").limit(1).execute()
            print("✅ user_settings表已存在")
        except Exception as e:
            if "table" in str(e).lower() and "not found" in str(e).lower():
                print("请在Supabase SQL编辑器中运行以下SQL:")
                print("""
                CREATE TABLE user_settings (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
                    preferred_model VARCHAR(100) DEFAULT 'gpt-3.5-turbo',
                    max_tokens INTEGER DEFAULT 1000,
                    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
                    chunk_size INTEGER DEFAULT 1000,
                    chunk_overlap INTEGER DEFAULT 200,
                    default_document_filter JSONB DEFAULT '[]',
                    ui_preferences JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                
                CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
                
                ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
                
                CREATE POLICY "Users can view own settings" ON user_settings FOR SELECT USING (auth.uid() = user_id);
                CREATE POLICY "Users can insert own settings" ON user_settings FOR INSERT WITH CHECK (auth.uid() = user_id);
                CREATE POLICY "Users can update own settings" ON user_settings FOR UPDATE USING (auth.uid() = user_id);
                """)
            else:
                print(f"检查user_settings表时出错: {e}")
        
        print("\n✅ 表创建脚本完成！")
        print("请在Supabase SQL编辑器中运行上述SQL语句来创建必要的表。")
        return True
        
    except Exception as e:
        print(f"❌ 创建表时出错: {e}")
        return False

def main():
    """主函数"""
    print("开始创建Supabase表...")
    
    if create_tables():
        print("🎉 表创建脚本执行成功！")
        return True
    else:
        print("⚠️  表创建脚本执行失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
