"""
详细诊断FireCrawl API问题
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_firecrawl_directly():
    """直接测试FireCrawl API"""

    # FireCrawl配置
    api_url = "http://192.168.1.2:8080/v1"
    target_url = "https://guba.eastmoney.com/list,300339,1,f.html"

    print(f"测试FireCrawl API: {api_url}")
    print(f"目标URL: {target_url}")

    # 构建请求
    payload = {
        "url": target_url,
        "formats": ["markdown"],
        "onlyMainContent": True
    }

    try:
        # 直接调用FireCrawl API
        response = requests.post(
            f"{api_url}/scrape",
            json=payload,
            timeout=30
        )

        print(f"HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"API响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")

            if data.get("success"):
                print("✅ API调用成功")

                # 检查返回的数据
                if "data" in data:
                    markdown_content = data["data"].get("markdown", "")
                    if markdown_content:
                        print(f"✅ 获取到markdown内容，长度: {len(markdown_content)} 字符")
                        print(f"内容预览: {markdown_content[:200]}...")
                    else:
                        print("❌ 没有获取到markdown内容")
                else:
                    print("❌ 响应中没有data字段")
            else:
                print(f"❌ API调用失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - FireCrawl服务可能没有运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()


def test_firecrawl_health():
    """测试FireCrawl服务健康状态"""

    api_url = "http://192.168.1.2:8080/v1"

    try:
        # 测试健康检查端点
        response = requests.get(f"{api_url}/health", timeout=10)
        print(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ FireCrawl服务运行正常")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到FireCrawl服务")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")


if __name__ == "__main__":
    print("=== FireCrawl服务健康检查 ===")
    test_firecrawl_health()

    print("\n=== 直接API调用测试 ===")
    test_firecrawl_directly()

