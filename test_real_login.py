#!/usr/bin/env python3
"""
测试真实登录流程的脚本
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_real_login():
    """测试真实的登录流程"""
    print("=== 测试真实登录流程 ===")
    
    # 测试注册
    print("1. 测试用户注册...")
    register_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "username": "testuser",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=register_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 用户注册成功")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 用户注册失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 注册请求失败: {e}")
        return False
    
    # 测试登录
    print("\n2. 测试用户登录...")
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 用户登录成功")
            login_response = response.json()
            print(f"响应: {login_response}")
            
            # 获取访问令牌
            access_token = login_response.get("access_token")
            if access_token:
                print("✅ 获取到访问令牌")
                
                # 测试获取用户信息
                print("\n3. 测试获取用户信息...")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                user_response = requests.get(
                    "http://localhost:8000/api/v1/users/me",
                    headers=headers,
                    timeout=10
                )
                
                if user_response.status_code == 200:
                    print("✅ 获取用户信息成功")
                    user_data = user_response.json()
                    print(f"用户信息: {user_data}")
                    return True
                else:
                    print(f"❌ 获取用户信息失败: {user_response.status_code}")
                    print(f"响应: {user_response.text}")
                    return False
            else:
                print("❌ 未获取到访问令牌")
                return False
        else:
            print(f"❌ 用户登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录请求失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试真实登录流程...")
    
    if test_real_login():
        print("\n🎉 登录流程测试成功！认证问题已完全修复。")
        return True
    else:
        print("\n⚠️  登录流程测试失败，请检查相关配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
