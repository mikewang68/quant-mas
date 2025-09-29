#!/usr/bin/env python3
"""
Comprehensive Pool Analyzer
Analyzes all strategies and signal generation results in the pool collection.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, List
import logging
import numpy as np
from collections import defaultdict

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

def comprehensive_pool_analysis(db) -> Dict[str, Any]:
    """
    Perform comprehensive analysis of the pool collection.

    Args:
        db: MongoDB database instance

    Returns:
        Dictionary with comprehensive analysis results
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

        logger.info(f"Performing comprehensive analysis on {len(pool_stocks)} stocks")

        # Initialize data structures
        results = {
            'pool_overview': {
                'total_stocks': len(pool_stocks),
                'field_distribution': defaultdict(int),
                'strategy_counts': defaultdict(int)
            },
            'strategy_analysis': {
                'scores_by_field': defaultdict(list),
                'score_statistics': {},
                'strategy_details': defaultdict(lambda: defaultdict(int))
            },
            'signal_generation': {
                'signal_stocks_count': 0,
                'score_statistics': {},
                'signal_distribution': {'买入': 0, '持有': 0, '卖出': 0},
                'signal_ai_distribution': {'买入': 0, '持有': 0, '卖出': 0},
                'top_stocks': [],
                'bottom_stocks': []
            },
            'correlation_analysis': {
                'strategy_signal_correlation': {}
            }
        }

        # Initialize score statistics
        score_stats = {
            'all_scores': [],
            'positive_scores': [],
            'zero_scores': [],
            'negative_scores': []
        }

        # Process each stock for strategy analysis
        for stock in pool_stocks:
            # Process all fields in the stock
            for field_name, field_value in stock.items():
                # Skip non-dict fields and excluded fields (code, signals)
                if field_name in ['code', 'signals'] or not isinstance(field_value, dict):
                    continue

                results['pool_overview']['field_distribution'][field_name] += 1

                # Process each strategy in the field
                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        full_strategy_name = f"{field_name}.{strategy_name}"
                        results['pool_overview']['strategy_counts'][full_strategy_name] += 1
                        results['strategy_analysis']['strategy_details'][field_name][strategy_name] += 1

                        # Collect scores for analysis
                        score = strategy_info.get('score')
                        if score is not None:
                            try:
                                score_float = float(score)
                                results['strategy_analysis']['scores_by_field'][field_name].append(score_float)
                                score_stats['all_scores'].append(score_float)

                                # Categorize scores
                                if score_float > 0:
                                    score_stats['positive_scores'].append(score_float)
                                elif score_float < 0:
                                    score_stats['negative_scores'].append(score_float)
                                else:
                                    score_stats['zero_scores'].append(score_float)

                            except (ValueError, TypeError):
                                pass  # Skip invalid scores

        # Process stocks for signal generation analysis
        signal_stocks = []
        signal_score_stats = {
            'all_scores': [],
            'scores_calc': [],
            'scores_ai': [],
        }

        for stock in pool_stocks:
            code = stock.get('code', 'Unknown')

            # Check if this stock has signal generation results
            if 'signals' in stock and '信号生成V1' in stock['signals']:
                signal_data = stock['signals']['信号生成V1']
                signal_stocks.append({
                    'code': code,
                    'data': signal_data
                })
                results['signal_generation']['signal_stocks_count'] += 1

                # Extract scores and signals
                score = signal_data.get('score', 0)
                value_data = signal_data.get('value', {})

                score_calc = value_data.get('score_calc', 0)
                signal_calc = value_data.get('signal_calc', '持有')
                score_ai = value_data.get('score_ai', 0)
                signal_ai = value_data.get('signal_ai', '持有')

                # Collect statistics
                signal_score_stats['all_scores'].append(score)
                signal_score_stats['scores_calc'].append(score_calc)
                signal_score_stats['scores_ai'].append(score_ai)

                # Count signals
                if signal_calc in results['signal_generation']['signal_distribution']:
                    results['signal_generation']['signal_distribution'][signal_calc] += 1
                if signal_ai in results['signal_generation']['signal_ai_distribution']:
                    results['signal_generation']['signal_ai_distribution'][signal_ai] += 1

        # Calculate strategy statistics
        for field_name, scores in results['strategy_analysis']['scores_by_field'].items():
            if scores:
                results['strategy_analysis']['score_statistics'][field_name] = {
                    'count': len(scores),
                    'average': np.mean(scores),
                    'median': np.median(scores),
                    'std_dev': np.std(scores),
                    'min': np.min(scores),
                    'max': np.max(scores)
                }

        # Calculate overall score statistics
        if score_stats['all_scores']:
            results['strategy_analysis']['score_statistics']['overall'] = {
                'total_scores': len(score_stats['all_scores']),
                'positive_scores': len(score_stats['positive_scores']),
                'zero_scores': len(score_stats['zero_scores']),
                'negative_scores': len(score_stats['negative_scores']),
                'overall_average': np.mean(score_stats['all_scores']),
                'overall_median': np.median(score_stats['all_scores']),
                'overall_std_dev': np.std(score_stats['all_scores']),
                'min_score': np.min(score_stats['all_scores']),
                'max_score': np.max(score_stats['all_scores'])
            }

        # Calculate signal generation statistics
        if signal_score_stats['all_scores']:
            results['signal_generation']['score_statistics'] = {
                'main_scores': {
                    'count': len(signal_score_stats['all_scores']),
                    'average': np.mean(signal_score_stats['all_scores']),
                    'median': np.median(signal_score_stats['all_scores']),
                    'std_dev': np.std(signal_score_stats['all_scores']),
                    'min': np.min(signal_score_stats['all_scores']),
                    'max': np.max(signal_score_stats['all_scores'])
                },
                'calc_scores': {
                    'count': len(signal_score_stats['scores_calc']),
                    'average': np.mean(signal_score_stats['scores_calc']),
                    'median': np.median(signal_score_stats['scores_calc']),
                    'std_dev': np.std(signal_score_stats['scores_calc']),
                    'min': np.min(signal_score_stats['scores_calc']),
                    'max': np.max(signal_score_stats['scores_calc'])
                },
                'ai_scores': {
                    'count': len(signal_score_stats['scores_ai']),
                    'average': np.mean(signal_score_stats['scores_ai']),
                    'median': np.median(signal_score_stats['scores_ai']),
                    'std_dev': np.std(signal_score_stats['scores_ai']),
                    'min': np.min(signal_score_stats['scores_ai']),
                    'max': np.max(signal_score_stats['scores_ai'])
                }
            }

        # Sort stocks by signal score to get top and bottom
        sorted_stocks = sorted(signal_stocks, key=lambda x: x['data'].get('score', 0), reverse=True)
        results['signal_generation']['top_stocks'] = sorted_stocks[:10]  # Top 10 stocks
        results['signal_generation']['bottom_stocks'] = sorted_stocks[-10:] if len(sorted_stocks) >= 10 else sorted_stocks[::-1][:10]  # Bottom 10 stocks

        return results

    except Exception as e:
        logger.error(f"Error performing comprehensive pool analysis: {e}")
        return {}

def print_comprehensive_analysis(results: Dict[str, Any]):
    """Print formatted comprehensive analysis results."""
    if not results:
        print("No results to display")
        return

    print("\n" + "="*80)
    print("COMPREHENSIVE POOL ANALYSIS REPORT")
    print("="*80)

    # Pool Overview
    overview = results.get('pool_overview', {})
    print(f"\nPool Overview:")
    print(f"  Total Stocks: {overview.get('total_stocks', 0)}")

    print(f"\nField Distribution:")
    field_dist = overview.get('field_distribution', {})
    for field, count in field_dist.items():
        print(f"  {field}: {count}")

    print(f"\nStrategy Counts:")
    strategy_counts = overview.get('strategy_counts', {})
    sorted_strategies = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)
    for strategy, count in sorted_strategies[:15]:  # Top 15 strategies
        print(f"  {strategy}: {count}")

    # Strategy Analysis
    strategy_analysis = results.get('strategy_analysis', {})
    print(f"\nStrategy Analysis:")

    print(f"\nOverall Score Statistics:")
    overall_stats = strategy_analysis.get('score_statistics', {}).get('overall', {})
    if overall_stats:
        print(f"  Total Scores: {overall_stats['total_scores']}")
        print(f"  Positive Scores: {overall_stats['positive_scores']} ({overall_stats['positive_scores']/overall_stats['total_scores']*100:.1f}%)")
        print(f"  Zero Scores: {overall_stats['zero_scores']} ({overall_stats['zero_scores']/overall_stats['total_scores']*100:.1f}%)")
        print(f"  Negative Scores: {overall_stats['negative_scores']} ({overall_stats['negative_scores']/overall_stats['total_scores']*100:.1f}%)")
        print(f"  Overall Average: {overall_stats['overall_average']:.4f}")
        print(f"  Overall Median: {overall_stats['overall_median']:.4f}")
        print(f"  Std Deviation: {overall_stats['overall_std_dev']:.4f}")
        print(f"  Score Range: {overall_stats['min_score']:.4f} to {overall_stats['max_score']:.4f}")

    print(f"\nScores by Field:")
    field_stats = strategy_analysis.get('score_statistics', {})
    for field_name, stats in field_stats.items():
        if field_name != 'overall':
            print(f"  {field_name}:")
            print(f"    Count: {stats['count']}")
            print(f"    Average: {stats['average']:.4f}")
            print(f"    Median: {stats['median']:.4f}")
            print(f"    Std Dev: {stats['std_dev']:.4f}")
            print(f"    Range: {stats['min']:.4f} to {stats['max']:.4f}")

    # Signal Generation Analysis
    signal_gen = results.get('signal_generation', {})
    print(f"\nSignal Generation Analysis:")
    print(f"  Stocks with Signal Generation Results: {signal_gen.get('signal_stocks_count', 0)} ({signal_gen.get('signal_stocks_count', 0)/overview.get('total_stocks', 1)*100:.1f}%)")

    print(f"\nSignal Generation Score Statistics:")
    sig_stats = signal_gen.get('score_statistics', {})
    if sig_stats:
        # Main scores
        main_stats = sig_stats.get('main_scores', {})
        if main_stats:
            print(f"  Main Scores (from 'score' field):")
            print(f"    Count: {main_stats['count']}")
            print(f"    Average: {main_stats['average']:.4f}")
            print(f"    Median: {main_stats['median']:.4f}")
            print(f"    Std Dev: {main_stats['std_dev']:.4f}")
            print(f"    Range: {main_stats['min']:.4f} to {main_stats['max']:.4f}")

        # Calculated scores
        calc_stats = sig_stats.get('calc_scores', {})
        if calc_stats:
            print(f"  Calculated Scores (from 'score_calc' field):")
            print(f"    Count: {calc_stats['count']}")
            print(f"    Average: {calc_stats['average']:.4f}")
            print(f"    Median: {calc_stats['median']:.4f}")
            print(f"    Std Dev: {calc_stats['std_dev']:.4f}")
            print(f"    Range: {calc_stats['min']:.4f} to {calc_stats['max']:.4f}")

        # AI scores
        ai_stats = sig_stats.get('ai_scores', {})
        if ai_stats:
            print(f"  AI Scores (from 'score_ai' field):")
            print(f"    Count: {ai_stats['count']}")
            print(f"    Average: {ai_stats['average']:.4f}")
            print(f"    Median: {ai_stats['median']:.4f}")
            print(f"    Std Dev: {ai_stats['std_dev']:.4f}")
            print(f"    Range: {ai_stats['min']:.4f} to {ai_stats['max']:.4f}")

    print(f"\nSignal Distribution (Calculated):")
    signal_dist = signal_gen.get('signal_distribution', {})
    total_signals = sum(signal_dist.values())
    for signal, count in signal_dist.items():
        percentage = (count / total_signals * 100) if total_signals > 0 else 0
        print(f"  {signal}: {count} ({percentage:.1f}%)")

    print(f"\nSignal Distribution (AI Generated):")
    signal_ai_dist = signal_gen.get('signal_ai_distribution', {})
    total_ai_signals = sum(signal_ai_dist.values())
    for signal, count in signal_ai_dist.items():
        percentage = (count / total_ai_signals * 100) if total_ai_signals > 0 else 0
        print(f"  {signal}: {count} ({percentage:.1f}%)")

    print(f"\nTop 10 Stocks by Signal Score:")
    for i, stock in enumerate(signal_gen.get('top_stocks', []), 1):
        code = stock.get('code', 'Unknown')
        score = stock.get('data', {}).get('score', 0)
        value_data = stock.get('data', {}).get('value', {})
        score_calc = value_data.get('score_calc', 0)
        signal_calc = value_data.get('signal_calc', '持有')
        score_ai = value_data.get('score_ai', 0)
        signal_ai = value_data.get('signal_ai', '持有')
        print(f"  {i:2d}. {code}: {score:.4f} (Calc: {score_calc:.4f}/{signal_calc}, AI: {score_ai:.4f}/{signal_ai})")

    print(f"\nBottom 10 Stocks by Signal Score:")
    for i, stock in enumerate(signal_gen.get('bottom_stocks', []), 1):
        code = stock.get('code', 'Unknown')
        score = stock.get('data', {}).get('score', 0)
        value_data = stock.get('data', {}).get('value', {})
        score_calc = value_data.get('score_calc', 0)
        signal_calc = value_data.get('signal_calc', '持有')
        score_ai = value_data.get('score_ai', 0)
        signal_ai = value_data.get('signal_ai', '持有')
        print(f"  {i:2d}. {code}: {score:.4f} (Calc: {score_calc:.4f}/{signal_calc}, AI: {score_ai:.4f}/{signal_ai})")

def main():
    """Main function to run the comprehensive analyzer."""
    print("Comprehensive Pool Analyzer")
    print("="*26)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Perform comprehensive analysis
    results = comprehensive_pool_analysis(db)

    # Print results
    print_comprehensive_analysis(results)

    return 0

if __name__ == "__main__":
    sys.exit(main())

