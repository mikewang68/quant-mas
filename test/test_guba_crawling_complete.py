"""
测试东方财富股吧数据爬取功能
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

from utils.eastmoney_guba_scraper import scrape_all_guba_data

def test_guba_data_crawling():
    """测试东方财富股吧数据爬取功能"""

    # FireCrawl配置
    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    # 测试股票代码
    test_stocks = ["000001", "000002", "000858"]

    for stock_code in test_stocks:
        try:
            logger.info(f"=== 开始测试股票 {stock_code} ===")

            # 爬取所有类型的数据
            all_data = scrape_all_guba_data(stock_code, firecrawl_config, limit_per_type=3)

            logger.info(f"股票 {stock_code} 爬取完成，获取到以下数据类型:")

            total_items = 0
            for data_type, data_list in all_data.items():
                logger.info(f"  {data_type}: {len(data_list)} 条数据")
                total_items += len(data_list)

                # 输出具体内容
                for i, item in enumerate(data_list, 1):
                    logger.info(f"    {i}. {item.get('title', 'N/A')}")
                    logger.info(f"       作者: {item.get('author', 'N/A')}")
                    logger.info(f"       阅读: {item.get('read_count', 'N/A')}, 评论: {item.get('comment_count', 'N/A')}")

            logger.info(f"股票 {stock_code} 总计获取 {total_items} 条数据")
            logger.info(f"=== 股票 {stock_code} 测试完成 ===\n")

        except Exception as e:
            logger.error(f"测试股票 {stock_code} 时出错: {e}")
            import traceback
            traceback.print_exc()

def test_individual_data_types():
    """测试单个数据类型爬取"""

    from utils.eastmoney_guba_scraper import scrape_guba_data

    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "000001"
    data_types = ["consultations", "research_reports", "announcements", "hot_posts"]

    logger.info(f"=== 测试单个数据类型爬取 (股票: {stock_code}) ===")

    for data_type in data_types:
        try:
            logger.info(f"测试数据类型: {data_type}")

            data = scrape_guba_data(stock_code, data_type, firecrawl_config, limit=2)

            logger.info(f"  {data_type} 获取到 {len(data)} 条数据:")
            for i, item in enumerate(data, 1):
                logger.info(f"    {i}. {item.get('title', 'N/A')}")

        except Exception as e:
            logger.error(f"测试数据类型 {data_type} 时出错: {e}")

    logger.info("=== 单个数据类型测试完成 ===\n")

if __name__ == "__main__":
    logger.info("开始测试东方财富股吧数据爬取功能")

    # 测试单个数据类型
    test_individual_data_types()

    # 测试完整爬取功能
    test_guba_data_crawling()

    logger.info("所有测试完成")

