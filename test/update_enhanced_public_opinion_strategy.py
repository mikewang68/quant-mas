#!/usr/bin/env python3
"""
Script to update the enhanced public opinion analysis strategy in the MongoDB database
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.mongodb_manager import MongoDBManager

def update_enhanced_public_opinion_strategy():
    """Update the enhanced public opinion analysis strategy in the database"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Define the updated enhanced public opinion analysis strategy
        updated_strategy = {
            "name": "增强型舆情分析策略",
            "type": "public_opinion",
            "description": "利用AkShare财经数据、专业金融网站、FireCrawl网络搜索和LLM情感分析来识别具有良好公众情绪的股票。该策略整合多个数据源，包括财经新闻、专业分析和社交媒体内容，通过大语言模型进行综合情感评估。",
            "parameters": {
                "sentiment_threshold": 0.6,
                "news_count_threshold": 5,
                "search_depth": 10,
                "time_window_hours": 24,
                "data_sources": ["akshare", "firecrawl", "professional_sites"],
                "professional_sites": [
                    "同花顺财经",
                    "东方财富网",
                    "雪球网",
                    "新浪财经",
                    "腾讯财经"
                ],
                "firecrawl_config": {
                    "api_url": "http://192.168.1.2:8080",
                    "timeout": 30,
                    "max_retries": 3,
                    "retry_delay": 1,
                    "rate_limit": 10,
                    "concurrent_requests": 5
                },
                "llm_config": {
                    "api_url": "",
                    "api_key_env_var": "GEMINI_API_KEY",
                    "model": "",
                    "timeout": 60
                }
            },
            "program": {
                "file": "enhanced_public_opinion_analysis_strategy",
                "class": "EnhancedPublicOpinionAnalysisStrategy"
            },
            "file": "enhanced_public_opinion_analysis_strategy",
            "class_name": "EnhancedPublicOpinionAnalysisStrategy",
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }

        # Update the strategy in the database
        result = db_manager.db.strategies.update_one(
            {"name": "增强型舆情分析策略"},
            {"$set": updated_strategy},
            upsert=True
        )

        if result.upserted_id or result.modified_count > 0:
            print(f"Successfully updated enhanced public opinion strategy")
            print(f"Strategy details:")
            print(f"  Name: {updated_strategy['name']}")
            print(f"  Type: {updated_strategy['type']}")
            print(f"  Description: {updated_strategy['description']}")
            print(f"  Program file: {updated_strategy['program']['file']}")
            print(f"  Program class: {updated_strategy['program']['class']}")
            print(f"  Professional sites: {updated_strategy['parameters']['professional_sites']}")
            print(f"  FireCrawl config: {updated_strategy['parameters']['firecrawl_config']}")
        else:
            print("No changes made to the strategy")

        # Close connection
        db_manager.close_connection()

    except Exception as e:
        print(f"Error updating enhanced public opinion strategy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_enhanced_public_opinion_strategy()

