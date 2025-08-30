#!/usr/bin/env python3
"""
简单的认证测试脚本
"""
import os
import sys
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_simple_auth():
    """简单的认证测试"""
    print("=== 简单认证测试 ===")
    
    # 测试后端健康状态
    print("1. 测试后端健康状态...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False
    
    # 测试认证端点（无效凭据）
    print("\n2. 测试认证端点...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"email": "test@test.com", "password": "wrongpassword"},
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ 认证端点正常（正确拒绝无效凭据）")
        else:
            print(f"❌ 认证端点异常: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 认证测试失败: {e}")
        return False
    
    # 测试注册端点（无效数据）
    print("\n3. 测试注册端点...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json={"email": "test@test.com", "password": "test123"},
            timeout=5
        )
        
        print(f"注册响应: {response.status_code}")
        if response.status_code in [200, 400, 422]:
            print("✅ 注册端点响应正常")
            if response.status_code == 400:
                print(f"响应内容: {response.text}")
        else:
            print(f"❌ 注册端点异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 注册测试失败: {e}")
        return False
    
    print("\n✅ 所有基本测试通过！")
    return True

def main():
    """主函数"""
    print("开始简单认证测试...")
    
    if test_simple_auth():
        print("\n🎉 认证系统基本功能正常！")
        print("\n下一步：")
        print("1. 检查Supabase项目配置")
        print("2. 确认邮箱验证设置")
        print("3. 测试真实用户注册和登录")
        return True
    else:
        print("\n⚠️  认证系统存在问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
