"""
简单测试东方财富股吧数据爬取功能
"""

import sys
import os
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_guba_crawling():
    """测试东方财富股吧数据爬取功能"""

    # FireCrawl配置
    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    # 测试股票代码
    stock_code = "000001"

    try:
        logger.info(f"=== 开始测试股票 {stock_code} ===")

        # 直接使用类方法测试
        from utils.eastmoney_guba_scraper import EastMoneyGubaScraper

        # 测试单个数据类型
        data_types = ["consultations", "research_reports", "announcements", "hot_posts"]

        for data_type in data_types:
            logger.info(f"测试数据类型: {data_type}")

            data = EastMoneyGubaScraper.scrape_eastmoney_guba(stock_code, data_type, firecrawl_config, limit=2)

            logger.info(f"  {data_type} 获取到 {len(data)} 条数据:")
            for i, item in enumerate(data, 1):
                logger.info(f"    {i}. {item.get('title', 'N/A')}")

        logger.info(f"=== 股票 {stock_code} 测试完成 ===\n")

    except Exception as e:
        logger.error(f"测试股票 {stock_code} 时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logger.info("开始测试东方财富股吧数据爬取功能")
    test_guba_crawling()
    logger.info("测试完成")

