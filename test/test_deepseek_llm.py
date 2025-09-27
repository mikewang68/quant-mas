#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek LLM 可用性测试程序
测试 DeepSeek API 的连接和基本功能
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek_connection():
    """测试 DeepSeek LLM 连接"""
    print("DeepSeek LLM 可用性测试")
    print("=" * 40)

    # 获取 API 密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误: 未找到 DEEPSEEK_API_KEY 环境变量")
        print("请设置 DEEPSEEK_API_KEY 环境变量后再运行测试")
        return False

    # API 配置
    api_url = "https://api.deepseek.com/v1/chat/completions"
    model = "deepseek-chat"

    try:
        print("正在测试 DeepSeek API 连接...")
        print(f"API URL: {api_url}")
        print(f"Model: {model}")
        print()

        # 准备请求数据
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test message. Please respond with 'Test successful'."},
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 100
        }

        # 发送测试请求
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        # 检查响应
        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                message = response_data["choices"][0]["message"]["content"]
                print("API 连接成功!")
                print(f"模型响应: {message}")
                print()
                print("DeepSeek LLM 测试完成 - 可用")
                return True
            else:
                print("错误: API 响应格式不正确")
                print(f"响应内容: {response_data}")
                return False
        else:
            print(f"错误: API 请求失败 - HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("错误: 连接 DeepSeek API 超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"错误: 连接 DeepSeek API 失败 - {str(e)}")
        return False
    except Exception as e:
        print(f"错误: 测试过程中发生异常 - {str(e)}")
        return False

def test_with_streaming():
    """测试流式响应"""
    print("\n流式响应测试")
    print("=" * 40)

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误: 未找到 DEEPSEEK_API_KEY 环境变量")
        return False

    # API 配置
    api_url = "https://api.deepseek.com/v1/chat/completions"
    model = "deepseek-chat"

    try:
        print("正在测试流式响应...")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Please briefly explain what artificial intelligence is in 2-3 sentences."},
            ],
            "stream": True,
            "temperature": 0.7
        }

        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30,
            stream=True
        )

        if response.status_code == 200:
            print("流式响应内容:")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data = decoded_line[6:]  # Remove 'data: ' prefix
                        if data != '[DONE]':
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_response += content
                                        print(content, end="", flush=True)
                            except json.JSONDecodeError:
                                continue

            print("\n")
            if full_response:
                print("流式响应测试成功!")
                return True
            else:
                print("错误: 流式响应为空")
                return False
        else:
            print(f"错误: 流式响应请求失败 - HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("错误: 流式响应请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"错误: 流式响应请求失败 - {str(e)}")
        return False
    except Exception as e:
        print(f"错误: 流式响应测试过程中发生异常 - {str(e)}")
        return False

def main():
    """主函数"""
    print("DeepSeek LLM 测试程序")
    print("确保已设置 DEEPSEEK_API_KEY 环境变量")
    print()

    # 基本连接测试
    success = test_deepseek_connection()

    if success:
        # 流式响应测试
        test_with_streaming()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

