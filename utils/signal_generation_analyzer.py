#!/usr/bin/env python3
"""
Signal Generation Strategy Analyzer
Analyzes the results of the Signal Generation V1 strategy in the pool collection.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, List
import logging
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB and return the database instance."""
    try:
        # Connection parameters from config/database.yaml
        MONGODB_URI = "mongodb://stock:681123@192.168.1.2:27017/admin"
        DATABASE_NAME = "stock"

        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None

def analyze_signal_generation_results(db) -> Dict[str, Any]:
    """
    Analyze Signal Generation V1 strategy results in the pool collection.

    Args:
        db: MongoDB database instance

    Returns:
        Dictionary with analysis results
    """
    try:
        # Get the pool collection
        pool_collection = db['pool']

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return {}

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        if not pool_stocks:
            logger.error("No stocks found in latest pool record")
            return {}

        logger.info(f"Analyzing {len(pool_stocks)} stocks for Signal Generation results")

        # Initialize counters and data structures
        signal_stocks = []
        score_stats = {
            'all_scores': [],
            'scores_calc': [],
            'scores_ai': [],
        }
        signal_counts = {
            '买入': 0,
            '持有': 0,
            '卖出': 0
        }
        signal_ai_counts = {
            '买入': 0,
            '持有': 0,
            '卖出': 0
        }

        # Process each stock
        for stock in pool_stocks:
            code = stock.get('code', 'Unknown')

            # Check if this stock has signal generation results
            if 'signals' in stock and '信号生成V1' in stock['signals']:
                signal_data = stock['signals']['信号生成V1']
                signal_stocks.append({
                    'code': code,
                    'data': signal_data
                })

                # Extract scores and signals
                score = signal_data.get('score', 0)
                value_data = signal_data.get('value', {})

                score_calc = value_data.get('score_calc', 0)
                signal_calc = value_data.get('signal_calc', '持有')
                score_ai = value_data.get('score_ai', 0)
                signal_ai = value_data.get('signal_ai', '持有')

                # Collect statistics
                score_stats['all_scores'].append(score)
                score_stats['scores_calc'].append(score_calc)
                score_stats['scores_ai'].append(score_ai)

                # Count signals
                if signal_calc in signal_counts:
                    signal_counts[signal_calc] += 1
                if signal_ai in signal_ai_counts:
                    signal_ai_counts[signal_ai] += 1

        logger.info(f"Found {len(signal_stocks)} stocks with Signal Generation results")

        # Calculate statistics
        results = {
            'total_stocks': len(pool_stocks),
            'signal_stocks_count': len(signal_stocks),
            'coverage_percentage': (len(signal_stocks) / len(pool_stocks)) * 100 if pool_stocks else 0,
            'score_statistics': {},
            'signal_distribution': signal_counts,
            'signal_ai_distribution': signal_ai_counts,
            'top_stocks': [],
            'bottom_stocks': []
        }

        # Calculate score statistics
        if score_stats['all_scores']:
            results['score_statistics'] = {
                'main_scores': {
                    'count': len(score_stats['all_scores']),
                    'average': np.mean(score_stats['all_scores']),
                    'median': np.median(score_stats['all_scores']),
                    'std_dev': np.std(score_stats['all_scores']),
                    'min': np.min(score_stats['all_scores']),
                    'max': np.max(score_stats['all_scores'])
                },
                'calc_scores': {
                    'count': len(score_stats['scores_calc']),
                    'average': np.mean(score_stats['scores_calc']),
                    'median': np.median(score_stats['scores_calc']),
                    'std_dev': np.std(score_stats['scores_calc']),
                    'min': np.min(score_stats['scores_calc']),
                    'max': np.max(score_stats['scores_calc'])
                },
                'ai_scores': {
                    'count': len(score_stats['scores_ai']),
                    'average': np.mean(score_stats['scores_ai']),
                    'median': np.median(score_stats['scores_ai']),
                    'std_dev': np.std(score_stats['scores_ai']),
                    'min': np.min(score_stats['scores_ai']),
                    'max': np.max(score_stats['scores_ai'])
                }
            }

        # Sort stocks by score to get top and bottom
        sorted_stocks = sorted(signal_stocks, key=lambda x: x['data'].get('score', 0), reverse=True)
        results['top_stocks'] = sorted_stocks[:10]  # Top 10 stocks
        results['bottom_stocks'] = sorted_stocks[-10:] if len(sorted_stocks) >= 10 else sorted_stocks[::-1][:10]  # Bottom 10 stocks

        return results

    except Exception as e:
        logger.error(f"Error analyzing signal generation results: {e}")
        return {}

def print_signal_analysis_results(results: Dict[str, Any]):
    """Print formatted signal generation analysis results."""
    if not results:
        print("No results to display")
        return

    print("\n" + "="*70)
    print("SIGNAL GENERATION V1 STRATEGY ANALYSIS REPORT")
    print("="*70)

    print(f"\nCoverage:")
    print(f"  Total Stocks in Pool: {results['total_stocks']}")
    print(f"  Stocks with Signal Generation Results: {results['signal_stocks_count']}")
    print(f"  Coverage Percentage: {results['coverage_percentage']:.2f}%")

    print(f"\nScore Statistics:")
    stats = results.get('score_statistics', {})
    if stats:
        # Main scores
        main_stats = stats.get('main_scores', {})
        if main_stats:
            print(f"  Main Scores (from 'score' field):")
            print(f"    Count: {main_stats['count']}")
            print(f"    Average: {main_stats['average']:.4f}")
            print(f"    Median: {main_stats['median']:.4f}")
            print(f"    Std Dev: {main_stats['std_dev']:.4f}")
            print(f"    Range: {main_stats['min']:.4f} to {main_stats['max']:.4f}")

        # Calculated scores
        calc_stats = stats.get('calc_scores', {})
        if calc_stats:
            print(f"  Calculated Scores (from 'score_calc' field):")
            print(f"    Count: {calc_stats['count']}")
            print(f"    Average: {calc_stats['average']:.4f}")
            print(f"    Median: {calc_stats['median']:.4f}")
            print(f"    Std Dev: {calc_stats['std_dev']:.4f}")
            print(f"    Range: {calc_stats['min']:.4f} to {calc_stats['max']:.4f}")

        # AI scores
        ai_stats = stats.get('ai_scores', {})
        if ai_stats:
            print(f"  AI Scores (from 'score_ai' field):")
            print(f"    Count: {ai_stats['count']}")
            print(f"    Average: {ai_stats['average']:.4f}")
            print(f"    Median: {ai_stats['median']:.4f}")
            print(f"    Std Dev: {ai_stats['std_dev']:.4f}")
            print(f"    Range: {ai_stats['min']:.4f} to {ai_stats['max']:.4f}")

    print(f"\nSignal Distribution (Calculated):")
    signal_dist = results.get('signal_distribution', {})
    total_signals = sum(signal_dist.values())
    for signal, count in signal_dist.items():
        percentage = (count / total_signals * 100) if total_signals > 0 else 0
        print(f"  {signal}: {count} ({percentage:.1f}%)")

    print(f"\nSignal Distribution (AI Generated):")
    signal_ai_dist = results.get('signal_ai_distribution', {})
    total_ai_signals = sum(signal_ai_dist.values())
    for signal, count in signal_ai_dist.items():
        percentage = (count / total_ai_signals * 100) if total_ai_signals > 0 else 0
        print(f"  {signal}: {count} ({percentage:.1f}%)")

    print(f"\nTop 10 Stocks by Signal Score:")
    for i, stock in enumerate(results.get('top_stocks', []), 1):
        code = stock.get('code', 'Unknown')
        score = stock.get('data', {}).get('score', 0)
        value_data = stock.get('data', {}).get('value', {})
        score_calc = value_data.get('score_calc', 0)
        signal_calc = value_data.get('signal_calc', '持有')
        score_ai = value_data.get('score_ai', 0)
        signal_ai = value_data.get('signal_ai', '持有')
        print(f"  {i:2d}. {code}: {score:.4f} (Calc: {score_calc:.4f}/{signal_calc}, AI: {score_ai:.4f}/{signal_ai})")

    print(f"\nBottom 10 Stocks by Signal Score:")
    for i, stock in enumerate(results.get('bottom_stocks', []), 1):
        code = stock.get('code', 'Unknown')
        score = stock.get('data', {}).get('score', 0)
        value_data = stock.get('data', {}).get('value', {})
        score_calc = value_data.get('score_calc', 0)
        signal_calc = value_data.get('signal_calc', '持有')
        score_ai = value_data.get('score_ai', 0)
        signal_ai = value_data.get('signal_ai', '持有')
        print(f"  {i:2d}. {code}: {score:.4f} (Calc: {score_calc:.4f}/{signal_calc}, AI: {score_ai:.4f}/{signal_ai})")

def main():
    """Main function to run the signal generation analyzer."""
    print("Signal Generation Strategy Analyzer")
    print("="*35)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Analyze signal generation results
    results = analyze_signal_generation_results(db)

    # Print results
    print_signal_analysis_results(results)

    return 0

if __name__ == "__main__":
    sys.exit(main())

