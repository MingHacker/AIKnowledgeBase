#!/usr/bin/env python3
"""
使用真实凭据测试登录的脚本
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_real_login():
    """使用真实凭据测试登录"""
    print("=== 使用真实凭据测试登录 ===")
    
    # 使用提供的真实凭据
    email = "byz_syz@hotmail.com"
    password = "jasLin324!"
    
    print(f"测试邮箱: {email}")
    print(f"密码: {'*' * len(password)}")
    
    # 测试登录
    print("\n1. 测试用户登录...")
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 用户登录成功！")
            login_response = response.json()
            print(f"响应内容: {json.dumps(login_response, indent=2)}")
            
            # 获取访问令牌
            access_token = login_response.get("access_token")
            if access_token:
                print("✅ 获取到访问令牌")
                print(f"令牌类型: {login_response.get('token_type', 'unknown')}")
                
                # 测试获取用户信息
                print("\n2. 测试获取用户信息...")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                user_response = requests.get(
                    "http://localhost:8000/api/v1/users/me",
                    headers=headers,
                    timeout=10
                )
                
                print(f"获取用户信息响应状态码: {user_response.status_code}")
                
                if user_response.status_code == 200:
                    print("✅ 获取用户信息成功！")
                    user_data = user_response.json()
                    print(f"用户信息: {json.dumps(user_data, indent=2, default=str)}")
                    
                    # 测试其他需要认证的端点
                    print("\n3. 测试其他认证端点...")
                    
                    # 测试获取用户设置
                    settings_response = requests.get(
                        "http://localhost:8000/api/v1/settings/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"获取用户设置: {settings_response.status_code}")
                    
                    # 测试获取文档列表
                    docs_response = requests.get(
                        "http://localhost:8000/api/v1/documents/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"获取文档列表: {docs_response.status_code}")
                    
                    return True
                else:
                    print(f"❌ 获取用户信息失败: {user_response.status_code}")
                    print(f"响应内容: {user_response.text}")
                    return False
            else:
                print("❌ 未获取到访问令牌")
                return False
        else:
            print(f"❌ 用户登录失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 登录请求失败: {e}")
        return False

def main():
    """主函数"""
    print("开始使用真实凭据测试登录...")
    
    if test_real_login():
        print("\n🎉 真实凭据登录测试成功！")
        print("认证系统已完全修复，可以正常处理用户登录和获取用户信息。")
        return True
    else:
        print("\n⚠️  真实凭据登录测试失败")
        print("可能的原因：")
        print("1. 用户不存在")
        print("2. 密码错误")
        print("3. 用户账户未激活")
        print("4. Supabase配置问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
