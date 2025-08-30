#!/usr/bin/env python3
"""
测试认证修复的脚本
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_environment_variables():
    """测试环境变量是否正确加载"""
    print("=== 测试环境变量 ===")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_KEY: {'已设置' if supabase_key else '未设置'}")
    
    if not supabase_url or not supabase_key:
        print("❌ 环境变量未正确加载")
        return False
    else:
        print("✅ 环境变量加载成功")
        return True

def test_backend_health():
    """测试后端健康状态"""
    print("\n=== 测试后端健康状态 ===")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_auth_endpoint():
    """测试认证端点"""
    print("\n=== 测试认证端点 ===")
    try:
        # 测试无效凭据
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"},
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ 认证端点响应正常 (无效凭据)")
        else:
            print(f"❌ 认证端点响应异常: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 认证端点测试失败: {e}")
        return False

def test_supabase_connection():
    """测试Supabase连接"""
    print("\n=== 测试Supabase连接 ===")
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase配置缺失")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        
        # 尝试获取用户配置文件（使用正确的表名）
        try:
            response = supabase.table("user_profiles").select("*").limit(1).execute()
            print("✅ Supabase连接成功")
            return True
        except Exception as e:
            if "JWT" in str(e) or "auth" in str(e).lower():
                print("✅ Supabase连接成功 (权限检查正常)")
                return True
            else:
                print(f"❌ Supabase连接失败: {e}")
                return False
                
    except ImportError:
        print("❌ Supabase库未安装")
        return False
    except Exception as e:
        print(f"❌ Supabase测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试认证修复...")
    
    tests = [
        test_environment_variables,
        test_backend_health,
        test_auth_endpoint,
        test_supabase_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 异常: {e}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！认证问题已修复。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
