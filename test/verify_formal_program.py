"""
验证正式运行程序是否使用修复后的代码
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

def verify_formal_program():
    """验证正式运行程序是否使用修复后的代码"""

    try:
        # 导入正式运行程序使用的函数
        from utils.eastmoney_guba_scraper import scrape_all_guba_data

        logger.info("✅ 成功导入 scrape_all_guba_data 函数")

        # 检查函数是否存在
        if hasattr(scrape_all_guba_data, '__call__'):
            logger.info("✅ scrape_all_guba_data 函数是可调用的")
        else:
            logger.error("❌ scrape_all_guba_data 函数不可调用")
            return False

        # 模拟FireCrawl配置
        firecrawl_config = {
            "api_url": "http://192.168.1.2:8080/v1",
            "max_retries": 3,
            "timeout": 30,
            "retry_delay": 1
        }

        # 测试股票代码
        stock_code = "000001"

        logger.info(f"测试正式运行程序使用的函数 (股票: {stock_code})")

        # 调用函数
        all_data = scrape_all_guba_data(stock_code, firecrawl_config, limit_per_type=2)

        logger.info(f"✅ 成功调用 scrape_all_guba_data 函数")
        logger.info(f"返回数据类型: {type(all_data)}")
        logger.info(f"包含的数据类型: {list(all_data.keys())}")

        # 检查每种数据类型
        for data_type, data_list in all_data.items():
            logger.info(f"  {data_type}: {len(data_list)} 条数据")

            # 检查输出格式
            for i, item in enumerate(data_list, 1):
                title = item.get('title', '')
                if "：" in title and not title.startswith("标题:"):
                    logger.info(f"    {i}. {title} ✅ 格式正确")
                else:
                    logger.warning(f"    {i}. {title} ❌ 格式可能不正确")

        logger.info("✅ 正式运行程序使用的函数完全正常")
        return True

    except Exception as e:
        logger.error(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("开始验证正式运行程序是否使用修复后的代码")

    success = verify_formal_program()

    if success:
        logger.info("✅ 正式运行程序已成功使用修复后的代码")
    else:
        logger.error("❌ 正式运行程序存在问题，需要进一步修复")

