import requests
import json
import time

def get_webrtc_ipv4_address_v2():
    """
    使用Firecrawl获取https://www.ident.me/网页中Browser data中的WebRTC addresses里的ipv4地址
    Firecrawl地址: 192.168.1.2:8080/v1
    这个版本增加了等待JavaScript执行的参数
    """

    # Firecrawl API端点
    firecrawl_url = "http://192.168.1.2:8080/v1/scrape"

    # 要抓取的网页
    target_url = "https://www.ident.me/"

    # 请求参数 - 增加等待JavaScript执行的参数
    payload = {
        "url": target_url,
        "formats": ["markdown", "html"],
        "waitFor": 5000,  # 等待5秒让JavaScript执行
        "pageOptions": {
            "waitFor": 5000  # 确保页面加载完成
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 发送POST请求到Firecrawl
        response = requests.post(firecrawl_url, json=payload, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是200会抛出异常

        # 解析响应数据
        data = response.json()

        print("Firecrawl响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 提取内容
        markdown_content = data.get('data', {}).get('markdown', '')
        html_content = data.get('data', {}).get('html', '')

        # 在内容中查找WebRTC IPv4地址
        # ident.me网站通常会直接显示IP地址信息
        # 我们需要在返回的内容中查找相关的IPv4地址信息

        # 查找可能包含WebRTC地址的部分
        if "webrtc" in markdown_content.lower() or "webrtc" in html_content.lower():
            print("\n检测到WebRTC相关信息")

        # 在内容中查找IPv4地址模式 (例如: 192.168.x.x 或 公网IP)
        import re
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv4_addresses = re.findall(ipv4_pattern, markdown_content + html_content)

        if ipv4_addresses:
            print(f"\n找到的IPv4地址:")
            unique_ips = list(set(ipv4_addresses))  # 去重
            for ip in unique_ips:
                # 验证IP地址格式是否正确
                octets = ip.split('.')
                if all(0 <= int(octet) <= 255 for octet in octets):
                    print(f"  - {ip}")

            # 过滤出可能是WebRTC地址的IP
            # 通常WebRTC会获取到本地IP(192.168.x.x, 10.x.x.x, 172.16-31.x.x)或公网IP
            webrtc_ips = []
            for ip in unique_ips:
                octets = ip.split('.')
                if all(0 <= int(octet) <= 255 for octet in octets):
                    # 排除回环地址和一些特殊地址
                    if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                        webrtc_ips.append(ip)

            print(f"\n可能的WebRTC IPv4地址:")
            for ip in webrtc_ips:
                print(f"  - {ip}")
            return webrtc_ips
        else:
            print("未找到IPv4地址")
            return []

    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"其他错误: {e}")
        return []

if __name__ == "__main__":
    print("使用Firecrawl获取ident.me网站的WebRTC IPv4地址...")
    print("等待JavaScript执行完成(最多5秒)...")
    ips = get_webrtc_ipv4_address_v2()
    if ips:
        print(f"\n成功获取到 {len(ips)} 个可能的WebRTC IPv4地址")
    else:
        print("\n未能获取到WebRTC IPv4地址")
        print("\n提示: ident.me网站的WebRTC地址是通过浏览器JavaScript动态获取的，")
        print("服务器端抓取可能无法获取到这些信息。")

