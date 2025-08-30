#!/usr/bin/env python3
"""
调试Supabase配置和权限的脚本
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
load_dotenv()

def debug_supabase():
    """调试Supabase配置和权限"""
    print("=== 调试Supabase配置和权限 ===")
    
    # 检查环境变量
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY: {'已设置' if supabase_key else '未设置'}")
    
    if not supabase_url or not supabase_key:
        print("❌ 环境变量缺失")
        return False
    
    try:
        # 创建Supabase客户端
        print("\n创建Supabase客户端...")
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase客户端创建成功")
        
        # 测试基本连接
        print("\n测试基本连接...")
        try:
            # 尝试获取用户列表（需要权限）
            response = supabase.auth.admin.list_users()
            print("✅ 管理员权限正常")
        except Exception as e:
            print(f"⚠️  管理员权限测试失败: {e}")
            
            # 尝试获取用户列表（普通权限）
            try:
                response = supabase.table("user_profiles").select("*").limit(1).execute()
                print("✅ 普通权限正常")
            except Exception as e2:
                print(f"❌ 普通权限测试失败: {e2}")
                
                # 检查是否是表不存在的问题
                if "table" in str(e2).lower() and "not found" in str(e2).lower():
                    print("❌ 表不存在，需要创建表")
                elif "JWT" in str(e2) or "auth" in str(e2).lower():
                    print("✅ 权限检查正常（需要认证）")
                else:
                    print(f"❌ 未知错误: {e2}")
        
        # 测试认证功能
        print("\n测试认证功能...")
        try:
            # 尝试注册用户
            auth_response = supabase.auth.sign_up({
                "email": "debug@example.com",
                "password": "debugpassword123"
            })
            
            if auth_response.user:
                print("✅ 用户注册功能正常")
                print(f"用户ID: {auth_response.user.id}")
                
                # 尝试登录
                login_response = supabase.auth.sign_in_with_password({
                    "email": "debug@example.com",
                    "password": "debugpassword123"
                })
                
                if login_response.user and login_response.session:
                    print("✅ 用户登录功能正常")
                    print(f"访问令牌: {login_response.session.access_token[:20]}...")
                    
                    # 尝试获取用户信息
                    user_response = supabase.auth.get_user(login_response.session.access_token)
                    if user_response.user:
                        print("✅ 获取用户信息功能正常")
                    else:
                        print("❌ 获取用户信息功能失败")
                else:
                    print("❌ 用户登录功能失败")
            else:
                print("❌ 用户注册功能失败")
                
        except Exception as e:
            print(f"❌ 认证功能测试失败: {e}")
            
            # 检查是否是邮箱确认问题
            if "email" in str(e).lower() and "confirm" in str(e).lower():
                print("⚠️  需要邮箱确认（这是正常的）")
            else:
                print(f"❌ 认证错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase调试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始调试Supabase...")
    
    if debug_supabase():
        print("\n✅ Supabase调试完成")
        return True
    else:
        print("\n❌ Supabase调试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
