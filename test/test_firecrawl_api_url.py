"""
测试FireCrawl API URL配置问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eastmoney_guba_scraper import EastMoneyGubaScraper


def test_firecrawl_api_url():
    """测试FireCrawl API URL配置"""

    # 测试配置
    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",  # 注意：这里没有包含/scrape
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    print(f"配置中的API URL: {firecrawl_config['api_url']}")
    print(f"实际调用的URL: {firecrawl_config['api_url']}/scrape")

    # 测试股票代码
    stock_code = "300339"

    print(f"\n测试股票: {stock_code}")

    try:
        # 测试爬取近期咨询
        consultations = EastMoneyGubaScraper.scrape_eastmoney_guba(
            stock_code=stock_code,
            data_type="consultations",
            firecrawl_config=firecrawl_config,
            limit=5
        )

        print(f"爬取结果: {len(consultations)} 条记录")

        if consultations:
            print("第一条记录:")
            print(f"  标题: {consultations[0]['title']}")
            print(f"  时间: {consultations[0]['publishedAt']}")
            print(f"  作者: {consultations[0]['author']}")
        else:
            print("没有获取到数据，可能是API调用失败或页面解析失败")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_firecrawl_api_url()

