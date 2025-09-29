#!/usr/bin/env python3
"""
Detailed Pool Analyzer
Analyzes strategies in the pool collection with detailed statistics.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, Tuple, List
import logging
from collections import defaultdict
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

def analyze_strategies_in_pool(db) -> Dict[str, Any]:
    """
    Analyze strategies in the pool collection with detailed statistics.

    Args:
        db: MongoDB database instance

    Returns:
        Dictionary with detailed analysis results
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

        logger.info(f"Analyzing {len(pool_stocks)} stocks from latest pool record")

        # Initialize counters and data structures
        total_strategy_count = 0
        scores_by_field = defaultdict(list)
        strategy_counts = defaultdict(int)
        score_stats = {
            'all_scores': [],
            'positive_scores': [],
            'zero_scores': [],
            'negative_scores': []
        }

        field_distribution = defaultdict(int)

        # Process each stock
        for stock in pool_stocks:
            # Process all fields in the stock
            for field_name, field_value in stock.items():
                # Skip non-dict fields and excluded fields (code, signals)
                if field_name in ['code', 'signals'] or not isinstance(field_value, dict):
                    continue

                field_distribution[field_name] += 1

                # Process each strategy in the field
                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        total_strategy_count += 1
                        full_strategy_name = f"{field_name}.{strategy_name}"
                        strategy_counts[full_strategy_name] += 1

                        # Try to get score for analysis
                        score = strategy_info.get('score')
                        if score is not None:
                            try:
                                score_float = float(score)
                                scores_by_field[field_name].append(score_float)
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

        # Calculate statistics
        results = {
            'total_stocks': len(pool_stocks),
            'total_strategies': total_strategy_count,
            'field_distribution': dict(field_distribution),
            'strategy_counts': dict(strategy_counts),
            'scores_by_field': {},
            'score_statistics': {},
            'top_strategies': []
        }

        # Calculate field-based statistics
        for field_name, scores in scores_by_field.items():
            if scores:
                results['scores_by_field'][field_name] = {
                    'count': len(scores),
                    'average': np.mean(scores),
                    'median': np.median(scores),
                    'std_dev': np.std(scores),
                    'min': np.min(scores),
                    'max': np.max(scores)
                }

        # Calculate overall score statistics
        if score_stats['all_scores']:
            results['score_statistics'] = {
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

        # Get top strategies by count
        sorted_strategies = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)
        results['top_strategies'] = sorted_strategies[:10]  # Top 10 strategies

        logger.info(f"Analysis complete. Found {total_strategy_count} strategies across {len(pool_stocks)} stocks")

        return results

    except Exception as e:
        logger.error(f"Error analyzing strategies in pool: {e}")
        return {}

def print_analysis_results(results: Dict[str, Any]):
    """Print formatted analysis results."""
    if not results:
        print("No results to display")
        return

    print("\n" + "="*60)
    print("DETAILED POOL ANALYSIS REPORT")
    print("="*60)

    print(f"\nPool Overview:")
    print(f"  Total Stocks: {results['total_stocks']}")
    print(f"  Total Strategies: {results['total_strategies']}")

    print(f"\nField Distribution:")
    for field, count in results['field_distribution'].items():
        print(f"  {field}: {count}")

    print(f"\nScore Statistics:")
    stats = results.get('score_statistics', {})
    if stats:
        print(f"  Total Scores: {stats['total_scores']}")
        print(f"  Positive Scores: {stats['positive_scores']} ({stats['positive_scores']/stats['total_scores']*100:.1f}%)")
        print(f"  Zero Scores: {stats['zero_scores']} ({stats['zero_scores']/stats['total_scores']*100:.1f}%)")
        print(f"  Negative Scores: {stats['negative_scores']} ({stats['negative_scores']/stats['total_scores']*100:.1f}%)")
        print(f"  Overall Average: {stats['overall_average']:.4f}")
        print(f"  Overall Median: {stats['overall_median']:.4f}")
        print(f"  Std Deviation: {stats['overall_std_dev']:.4f}")
        print(f"  Score Range: {stats['min_score']:.4f} to {stats['max_score']:.4f}")

    print(f"\nScores by Field:")
    for field, field_stats in results.get('scores_by_field', {}).items():
        print(f"  {field}:")
        print(f"    Count: {field_stats['count']}")
        print(f"    Average: {field_stats['average']:.4f}")
        print(f"    Median: {field_stats['median']:.4f}")
        print(f"    Std Dev: {field_stats['std_dev']:.4f}")
        print(f"    Range: {field_stats['min']:.4f} to {field_stats['max']:.4f}")

    print(f"\nTop 10 Strategies by Count:")
    for strategy, count in results['top_strategies']:
        print(f"  {strategy}: {count}")

def main():
    """Main function to run the analyzer."""
    print("Detailed Pool Analyzer")
    print("="*20)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Analyze strategies
    results = analyze_strategies_in_pool(db)

    # Print results
    print_analysis_results(results)

    return 0

if __name__ == "__main__":
    sys.exit(main())

