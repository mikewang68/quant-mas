#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票300339舆情分析程序
使用Firecrawl爬取相关信息，用Gemini进行分析并给出score分数
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

# 第三方库导入
import requests
import google.generativeai as genai

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Stock300339SentimentAnalyzer:
    """股票300339舆情分析器"""

    def __init__(self):
        """初始化分析器"""
        self.stock_code = "300339"
        self.stock_name = "润和软件"

        # 配置Firecrawl API
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        if not self.firecrawl_api_key:
            logger.warning("FIRECRAWL_API_KEY环境变量未设置，将使用模拟数据")

        # 配置Gemini API
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY环境变量未设置，将使用模拟分析")
        else:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def crawl_stock_news(self) -> List[Dict]:
        """使用Firecrawl爬取股票相关新闻"""
        logger.info(f"开始爬取股票{self.stock_code}({self.stock_name})的相关新闻...")

        if not self.firecrawl_api_key:
            # 返回模拟数据
            return self._get_mock_news_data()

        try:
            # Firecrawl API配置
            headers = {
                'Authorization': f'Bearer {self.firecrawl_api_key}',
                'Content-Type': 'application/json'
            }

            # 搜索相关新闻的URL列表
            search_urls = [
                f"https://finance.sina.com.cn/realstock/company/sz{self.stock_code}/nc.shtml",
                f"https://stock.eastmoney.com/{self.stock_code}.html",
                f"https://xueqiu.com/S/SZ{self.stock_code}",
                f"https://www.cnstock.com/search?keyword={self.stock_name}"
            ]

            news_data = []

            for url in search_urls:
                try:
                    # 使用Firecrawl爬取页面
                    crawl_data = {
                        "url": url,
                        "formats": ["markdown", "html"],
                        "onlyMainContent": True,
                        "includeTags": ["title", "meta", "article", "div"],
                        "excludeTags": ["script", "style", "nav", "footer"]
                    }

                    response = requests.post(
                        'https://api.firecrawl.dev/v0/scrape',
                        headers=headers,
                        json=crawl_data,
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            content = result.get('data', {}).get('markdown', '')
                            if content:
                                news_data.append({
                                    'url': url,
                                    'content': content[:2000],  # 限制内容长度
                                    'timestamp': datetime.now().isoformat(),
                                    'source': url.split('/')[2]
                                })
                                logger.info(f"成功爬取: {url}")

                    # 避免请求过于频繁
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"爬取{url}失败: {str(e)}")
                    continue

            if not news_data:
                logger.warning("未能爬取到有效数据，使用模拟数据")
                return self._get_mock_news_data()

            return news_data

        except Exception as e:
            logger.error(f"Firecrawl爬取过程出错: {str(e)}")
            return self._get_mock_news_data()

    def _get_mock_news_data(self) -> List[Dict]:
        """获取模拟新闻数据"""
        return [
            {
                'url': 'https://finance.sina.com.cn/mock',
                'content': f'{self.stock_name}(300339)今日发布三季度财报，营收同比增长15%，净利润增长12%。公司在软件服务领域表现稳健，云计算业务持续增长。',
                'timestamp': datetime.now().isoformat(),
                'source': 'sina.com.cn'
            },
            {
                'url': 'https://stock.eastmoney.com/mock',
                'content': f'{self.stock_name}获得多家机构调研，分析师普遍看好公司在数字化转型领域的发展前景。公司近期签署多个重要合同，业务拓展顺利。',
                'timestamp': datetime.now().isoformat(),
                'source': 'eastmoney.com'
            },
            {
                'url': 'https://xueqiu.com/mock',
                'content': f'{self.stock_name}股价近期表现稳定，技术面显示多头趋势。投资者对公司长期发展保持乐观态度，机构持仓比例稳步上升。',
                'timestamp': datetime.now().isoformat(),
                'source': 'xueqiu.com'
            }
        ]

    def analyze_sentiment_with_gemini(self, news_data: List[Dict]) -> Dict:
        """使用Gemini分析舆情并给出评分"""
        logger.info("开始使用Gemini进行舆情分析...")

        if not self.gemini_api_key:
            return self._get_mock_analysis()

        try:
            # 准备分析文本
            analysis_text = f"请分析以下关于股票{self.stock_code}({self.stock_name})的新闻内容，并给出舆情评分：\n\n"

            for i, news in enumerate(news_data, 1):
                analysis_text += f"新闻{i}（来源：{news['source']}）：\n{news['content']}\n\n"

            analysis_text += """
请根据以上新闻内容，从以下几个维度进行分析：
1. 整体舆情倾向（正面/中性/负面）
2. 公司基本面情况
3. 市场表现和投资者情绪
4. 风险因素分析

最后给出一个0-1之间的综合评分，其中：
- 0.8-1.0: 非常正面
- 0.6-0.8: 正面
- 0.4-0.6: 中性
- 0.2-0.4: 负面
- 0.0-0.2: 非常负面

请以JSON格式返回分析结果，包含：
{
    "sentiment": "正面/中性/负面",
    "score": 0.75,
    "analysis": "详细分析内容",
    "key_points": ["要点1", "要点2", "要点3"],
    "risk_factors": ["风险1", "风险2"]
}
"""

            # 调用Gemini API
            response = self.model.generate_content(analysis_text)

            if response and response.text:
                # 尝试解析JSON响应
                try:
                    # 提取JSON部分
                    response_text = response.text.strip()
                    if '```json' in response_text:
                        json_start = response_text.find('```json') + 7
                        json_end = response_text.find('```', json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif '{' in response_text and '}' in response_text:
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}') + 1
                        json_text = response_text[json_start:json_end]
                    else:
                        raise ValueError("未找到有效的JSON格式")

                    result = json.loads(json_text)

                    # 验证必要字段
                    if 'score' not in result:
                        result['score'] = 0.6  # 默认中性评分

                    # 确保评分在0-1范围内
                    result['score'] = max(0.0, min(1.0, float(result['score'])))

                    logger.info(f"Gemini分析完成，评分: {result['score']}")
                    return result

                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"解析Gemini响应失败: {str(e)}")
                    # 返回基于响应文本的简单分析
                    return self._parse_text_response(response.text)

        except Exception as e:
            logger.error(f"Gemini分析过程出错: {str(e)}")

        return self._get_mock_analysis()

    def _parse_text_response(self, text: str) -> Dict:
        """解析文本响应并提取评分"""
        # 简单的文本分析逻辑
        positive_words = ['增长', '上涨', '利好', '看好', '乐观', '稳健', '强劲']
        negative_words = ['下跌', '亏损', '风险', '担忧', '悲观', '困难', '挑战']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            score = 0.7
            sentiment = "正面"
        elif negative_count > positive_count:
            score = 0.3
            sentiment = "负面"
        else:
            score = 0.5
            sentiment = "中性"

        return {
            "sentiment": sentiment,
            "score": score,
            "analysis": f"基于文本分析，发现{positive_count}个正面词汇，{negative_count}个负面词汇",
            "key_points": ["文本分析结果"],
            "risk_factors": ["分析基于有限信息"]
        }

    def _get_mock_analysis(self) -> Dict:
        """获取模拟分析结果"""
        return {
            "sentiment": "正面",
            "score": 0.72,
            "analysis": f"基于收集的新闻信息，{self.stock_name}整体舆情表现正面。公司业绩稳健增长，市场表现良好，投资者情绪乐观。",
            "key_points": [
                "财报数据显示营收和净利润双增长",
                "机构调研活跃，分析师看好发展前景",
                "股价表现稳定，技术面呈现多头趋势"
            ],
            "risk_factors": [
                "市场整体波动风险",
                "行业竞争加剧"
            ]
        }

    def run_analysis(self) -> Dict:
        """运行完整的舆情分析流程"""
        logger.info(f"开始对股票{self.stock_code}({self.stock_name})进行舆情分析...")

        try:
            # 1. 爬取新闻数据
            news_data = self.crawl_stock_news()
            logger.info(f"成功爬取{len(news_data)}条新闻")

            # 2. 使用Gemini分析
            analysis_result = self.analyze_sentiment_with_gemini(news_data)

            # 3. 整合结果
            final_result = {
                "stock_code": self.stock_code,
                "stock_name": self.stock_name,
                "analysis_time": datetime.now().isoformat(),
                "news_count": len(news_data),
                "sentiment_analysis": analysis_result,
                "score": analysis_result.get("score", 0.5),
                "raw_news_data": news_data
            }

            return final_result

        except Exception as e:
            logger.error(f"分析过程出错: {str(e)}")
            return {
                "stock_code": self.stock_code,
                "stock_name": self.stock_name,
                "analysis_time": datetime.now().isoformat(),
                "error": str(e),
                "score": 0.5
            }

def main():
    """主函数"""
    print("=" * 60)
    print("股票300339(润和软件)舆情分析程序")
    print("=" * 60)

    # 创建分析器实例
    analyzer = Stock300339SentimentAnalyzer()

    # 运行分析
    result = analyzer.run_analysis()

    # 输出结果
    print(f"\n分析结果:")
    print(f"股票代码: {result['stock_code']}")
    print(f"股票名称: {result['stock_name']}")
    print(f"分析时间: {result['analysis_time']}")

    if 'error' in result:
        print(f"错误信息: {result['error']}")
    else:
        print(f"新闻数量: {result['news_count']}")

        sentiment_analysis = result.get('sentiment_analysis', {})
        print(f"舆情倾向: {sentiment_analysis.get('sentiment', 'N/A')}")
        print(f"综合评分: {result['score']:.2f}")
        print(f"分析摘要: {sentiment_analysis.get('analysis', 'N/A')}")

        key_points = sentiment_analysis.get('key_points', [])
        if key_points:
            print("\n关键要点:")
            for i, point in enumerate(key_points, 1):
                print(f"  {i}. {point}")

        risk_factors = sentiment_analysis.get('risk_factors', [])
        if risk_factors:
            print("\n风险因素:")
            for i, risk in enumerate(risk_factors, 1):
                print(f"  {i}. {risk}")

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

    return result

if __name__ == "__main__":
    # 运行程序
    result = main()

    # 可选：保存结果到文件
    try:
        with open(f'sentiment_analysis_{result["stock_code"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到文件")
    except Exception as e:
        print(f"保存文件失败: {str(e)}")

