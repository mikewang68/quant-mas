#!/usr/bin/env python3
"""
Insert a new record for Enhanced Public Opinion Analysis Strategy V2 into the strategies collection
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from config.mongodb_config import MongoDBConfig

def insert_enhanced_public_opinion_v2_strategy():
    """Insert the Enhanced Public Opinion Analysis Strategy V2 record"""
    try:
        # Load MongoDB configuration
        mongodb_config = MongoDBConfig()
        config = mongodb_config.get_mongodb_config()

        # Connect to MongoDB
        if config.get('username') and config.get('password'):
            # With authentication
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
        else:
            # Without authentication
            uri = f"mongodb://{config['host']}:{config['port']}/"

        client = MongoClient(uri)
        db = client[config['database']]

        # Get the strategies collection name
        strategies_collection_name = mongodb_config.get_collection_name('strategies')
        strategies_collection = db[strategies_collection_name]

        # Define the new strategy record
        new_strategy = {
            "name": "增强型舆情分析策略V2",
            "type": "sentiment",
            "description": "利用AkShare财经数据、专业金融网站、FireCrawl网络搜索、东方财富股吧数据和LLM情感分析来识别具有良好公众情绪的股票。该策略整合多个数据源，包括财经新闻、专业分析、股吧讨论和社交媒体内容，通过大语言模型进行综合情感评估。",
            "parameters": {
                "data_sources": ["akshare", "firecrawl", "professional_sites", "guba"],
                "firecrawl_config": {
                    "api_url": "http://192.168.1.2:8080",
                    "timeout": 30,
                    "max_retries": 3,
                    "retry_delay": 1,
                    "rate_limit": 10,
                    "concurrent_requests": 5
                },
                "llm_name": "gemini-2.0-flash",
                "news_count_threshold": 5,
                "professional_sites": [
                    "同花顺财经",
                    "东方财富网",
                    "雪球网",
                    "新浪财经",
                    "腾讯财经"
                ],
                "search_depth": 10,
                "sentiment_threshold": 0.6,
                "time_window_hours": 24
            },
            "program": {
                "file": "enhanced_public_opinion_analysis_strategy_v2",
                "class": "EnhancedPublicOpinionAnalysisStrategyV2"
            },
            "file": "enhanced_public_opinion_analysis_strategy_v2",
            "class_name": "EnhancedPublicOpinionAnalysisStrategyV2",
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }

        # Insert the new record
        result = strategies_collection.insert_one(new_strategy)

        if result.inserted_id:
            print("Successfully inserted Enhanced Public Opinion Analysis Strategy V2")
            print(f"Inserted document ID: {result.inserted_id}")
        else:
            print("Failed to insert the new strategy record")

        client.close()

    except Exception as e:
        print(f"Error inserting strategy record: {e}")
        sys.exit(1)

if __name__ == "__main__":
    insert_enhanced_public_opinion_v2_strategy()

