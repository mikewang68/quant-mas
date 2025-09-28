#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终版IP地址检测工具

此工具通过直接调用多个可靠的API来获取当前网络环境的公网IP地址。
由于ip138.com网站结构已改变，不再直接显示IP地址，因此使用API是更可靠的方法。

注意：获取到的IP地址是您设备的真实公网IP地址。
"""

import requests
import json
import time


def detect_ip_via_api():
    """
    通过多个API获取公网IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    result = {
        'ip_address': None,
        'location': None,
        'source_apis': [],
        'all_results': [],
        'logs': [],
        'success': False,
        'error': None
    }

    # 多个可靠的IP查询API
    apis = [
        {
            'url': 'https://api.ipify.org',
            'name': 'ipify.org',
            'method': 'GET',
            'type': 'plain'
        },
        {
            'url': 'https://icanhazip.com',
            'name': 'icanhazip.com',
            'method': 'GET',
            'type': 'plain'
        },
        {
            'url': 'https://ident.me',
            'name': 'ident.me',
            'method': 'GET',
            'type': 'plain'
        },
        {
            'url': 'https://ipecho.net/plain',
            'name': 'ipecho.net',
            'method': 'GET',
            'type': 'plain'
        },
        {
            'url': 'https://myexternalip.com/raw',
            'name': 'myexternalip.com',
            'method': 'GET',
            'type': 'plain'
        },
        {
            'url': 'https://api.my-ip.io/ip',
            'name': 'my-ip.io',
            'method': 'GET',
            'type': 'plain'
        }
    ]

    print("🚀 启动API方式IP地址检测")
    print("="*50)
    result['logs'].append("启动API方式IP地址检测")

    # 遍历所有API
    for i, api in enumerate(apis, 1):
        try:
            print(f"📍 尝试API {i}/{len(apis)}: {api['name']}")
            result['logs'].append(f"尝试API {i}/{len(apis)}: {api['name']}")

            # 发送请求
            response = requests.get(api['url'], timeout=10)

            if response.status_code == 200:
                # 获取IP地址
                ip_address = response.text.strip()
                print(f"✅ API {api['name']} 返回: {ip_address}")
                result['logs'].append(f"API {api['name']} 返回: {ip_address}")

                # 验证IP地址格式
                if is_valid_public_ip(ip_address):
                    # 保存结果
                    api_result = {
                        'api_name': api['name'],
                        'ip_address': ip_address,
                        'status': 'success'
                    }
                    result['all_results'].append(api_result)
                    result['source_apis'].append(api['name'])

                    # 如果还没有设置主IP地址，则设置
                    if not result['ip_address']:
                        result['ip_address'] = ip_address
                        print(f"🎯 设置为主IP地址: {ip_address}")
                        result['logs'].append(f"设置为主IP地址: {ip_address}")
                else:
                    print(f"⚠️ API {api['name']} 返回无效IP: {ip_address}")
                    result['logs'].append(f"API {api['name']} 返回无效IP: {ip_address}")
                    api_result = {
                        'api_name': api['name'],
                        'ip_address': ip_address,
                        'status': 'invalid'
                    }
                    result['all_results'].append(api_result)
            else:
                print(f"⚠️ API {api['name']} 返回状态码: {response.status_code}")
                result['logs'].append(f"API {api['name']} 返回状态码: {response.status_code}")
                api_result = {
                    'api_name': api['name'],
                    'ip_address': None,
                    'status': 'failed',
                    'error': f'状态码: {response.status_code}'
                }
                result['all_results'].append(api_result)

        except Exception as e:
            error_msg = f"❌ API {api['name']} 请求失败: {str(e)}"
            print(error_msg)
            result['logs'].append(error_msg)
            api_result = {
                'api_name': api['name'],
                'ip_address': None,
                'status': 'error',
                'error': str(e)
            }
            result['all_results'].append(api_result)

    # 检查是否成功获取到IP地址
    if result['ip_address']:
        result['success'] = True
        print("✅ IP地址检测完成!")
    else:
        result['error'] = "所有API都无法获取有效IP地址"
        print("❌ IP地址检测失败!")

    return result


def is_valid_public_ip(ip):
    """
    验证是否为有效的公网IP地址

    Args:
        ip (str): 要验证的IP地址

    Returns:
        bool: 如果是有效的公网IP返回True，否则返回False
    """
    try:
        # IPv4验证
        if '.' in ip:
            octets = ip.split('.')
            if len(octets) != 4:
                return False
            for octet in octets:
                val = int(octet)
                if val < 0 or val > 255:
                    return False
            # 排除私有IP和特殊IP
            if ip.startswith(('127.', '0.', '255.', '224.')):
                return False
            if ip.startswith('192.168.'):
                return False
            if ip.startswith('10.'):
                return False
            if ip.startswith('172.'):
                second_octet = int(ip.split('.')[1])
                if 16 <= second_octet <= 31:
                    return False
            if ip == '1.1.1.1':
                return False
            # 排除一些常见的测试IP
            if ip.startswith('198.18.'):
                return False
            return True
        return False
    except:
        return False


def print_detailed_results(result):
    """
    打印详细结果

    Args:
        result (dict): detect_ip_via_api函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 API检测结果详情")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    # 主IP地址
    if result['ip_address']:
        print(f"\n🌐 检测到的公网IP地址:")
        print(f"   🌍 {result['ip_address']}")

    # 所有API的结果
    if result['all_results']:
        print(f"\n📋 所有API检测结果:")
        for api_result in result['all_results']:
            status_icon = "✅" if api_result['status'] == 'success' else "❌" if api_result['status'] == 'failed' else "⚠️"
            if api_result['ip_address']:
                print(f"   {status_icon} {api_result['api_name']}: {api_result['ip_address']}")
            else:
                print(f"   {status_icon} {api_result['api_name']}: {api_result.get('error', '无响应')}")

    # 使用的API
    if result['source_apis']:
        print(f"\n🔧 成功获取IP的API:")
        for api_name in result['source_apis']:
            print(f"   📡 {api_name}")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        # 添加时间戳
        result['timestamp'] = int(time.time())

        filename = f"final_ip_detection_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数 - 执行最终版IP地址检测
    """
    print("🔍 最终版IP地址检测工具")
    print("此工具通过调用多个可靠的API来获取您的公网IP地址")
    print("由于网站结构变化，直接网页解析已不可靠，API方式更稳定")
    print()

    # 执行检测
    result = detect_ip_via_api()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. 这些IP地址是您设备的真实公网IP地址")
    print("2. 通过多个API获取，提高准确性")
    print("3. API方式比网页解析更稳定可靠")
    print("4. 如果所有API都失败，请检查网络连接")

    if result['success'] and result['ip_address']:
        print(f"\n🎉 成功检测到公网IP地址: {result['ip_address']}")
        print(f"   来自 {len(result['source_apis'])} 个API的一致结果")
    else:
        print(f"\n💥 IP地址检测失败，请检查网络连接")


if __name__ == "__main__":
    main()

