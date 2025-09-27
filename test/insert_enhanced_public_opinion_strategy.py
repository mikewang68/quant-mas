#!/usr/bin/env python3
"""
Script to insert the enhanced public opinion analysis strategy into the MongoDB database
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.mongodb_manager import MongoDBManager

def insert_enhanced_public_opinion_strategy():
    """Insert the enhanced public opinion analysis strategy into the database"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Define the enhanced public opinion analysis strategy
        enhanced_strategy = {
            "name": "增强型舆情分析策略",
            "type": "public_opinion",
            "description": "利用AkShare财经数据、专业金融网站、FireCrawl网络搜索和LLM情感分析来识别具有良好公众情绪的股票。该策略整合多个数据源，包括财经新闻、专业分析和社交媒体内容，通过大语言模型进行综合情感评估。",
            "parameters": {
                "sentiment_threshold": 0.6,
                "news_count_threshold": 5,
                "search_depth": 10,
                "time_window_hours": 24,
                "data_sources": ["akshare", "firecrawl", "professional_sites"]
            },
            "program": {
                "file": "enhanced_public_opinion_analysis_strategy",
                "class": "EnhancedPublicOpinionAnalysisStrategy"
            },
            "file": "enhanced_public_opinion_analysis_strategy",
            "class_name": "EnhancedPublicOpinionAnalysisStrategy",
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }

        # Insert the strategy into the database
        result = db_manager.db.strategies.insert_one(enhanced_strategy)

        if result.inserted_id:
            print(f"Successfully inserted enhanced public opinion strategy with ID: {result.inserted_id}")
            print(f"Strategy details:")
            print(f"  Name: {enhanced_strategy['name']}")
            print(f"  Type: {enhanced_strategy['type']}")
            print(f"  Description: {enhanced_strategy['description']}")
            print(f"  Program file: {enhanced_strategy['program']['file']}")
            print(f"  Program class: {enhanced_strategy['program']['class']}")
        else:
            print("Failed to insert strategy")

        # Close connection
        db_manager.close_connection()

    except Exception as e:
        print(f"Error inserting enhanced public opinion strategy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insert_enhanced_public_opinion_strategy()

