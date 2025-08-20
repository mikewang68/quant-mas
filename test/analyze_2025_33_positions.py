#!/usr/bin/env python3
"""
Analyze position calculation specifically for the 2025-33 record (Accelerating Uptrend Strategy)
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json
import numpy as np

def analyze_2025_33_positions():
    """Analyze position calculation for the 2025-33 record"""
    print("Analyzing position calculation for the 2025-33 record (Accelerating Uptrend Strategy)...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get the specific record 2025-33
        record = pool_collection.find_one({'_id': '2025-33'})

        if not record:
            print("Record 2025-33 not found")
            return False

        print(f"\nRecord 2025-33:")
        print(f"  Strategy Name: {record.get('strategy_name', 'N/A')}")
        print(f"  Selection Date: {record.get('selection_date', 'N/A')}")
        print(f"  Total Stocks: {record.get('count', 'N/A')}")

        # Analyze stocks with nested positions
        stocks = record.get('stocks', [])
        stocks_with_nested_position = []

        for stock in stocks:
            tech_analysis = stock.get('tech_analysis', {})
            acc_up_trend = tech_analysis.get('acc_up_trend', {})
            if 'position' in acc_up_trend:
                stocks_with_nested_position.append({
                    'code': stock.get('code', 'N/A'),
                    'position': acc_up_trend['position'],
                    'technical_data': acc_up_trend,
                    'original_stock': stock
                })

        print(f"\nFound {len(stocks_with_nested_position)} stocks with nested positions")

        if stocks_with_nested_position:
            print(f"\nAnalyzing position calculation based on Accelerating Uptrend Strategy:")

            # According to the strategy's calculate_position_size method:
            # position = (portfolio_value * 0.1) / price
            # Therefore: price = (portfolio_value * 0.1) / position

            # Let's assume a typical portfolio value and see if the implied prices are reasonable
            portfolio_values = [100000, 500000, 1000000, 5000000]  # Different portfolio sizes

            print(f"\nImplied stock prices based on different portfolio values:")
            print(f"{'Stock':<8} {'Position':<10} {'Price@100K':<10} {'Price@500K':<10} {'Price@1M':<10} {'Price@5M':<10}")

            # Analyze first 10 stocks
            for i, stock_info in enumerate(stocks_with_nested_position[:10]):
                code = stock_info['code']
                position = stock_info['position']

                # Calculate implied prices for different portfolio values
                implied_prices = []
                for portfolio_value in portfolio_values:
                    implied_price = (portfolio_value * 0.1) / position
                    implied_prices.append(implied_price)

                print(f"{code:<8} {position:<10.2f} {implied_prices[0]:<10.2f} {implied_prices[1]:<10.2f} "
                      f"{implied_prices[2]:<10.2f} {implied_prices[3]:<10.2f}")

            # Check if there's a consistent portfolio value
            print(f"\nChecking for consistent portfolio value assumption:")

            # For each stock, calculate what portfolio value would result in a "reasonable" price
            # Let's assume a reasonable price range is 5-100 RMB
            reasonable_prices = range(5, 101, 5)

            print(f"\nPortfolio values that would result in reasonable prices (5-100 RMB):")
            print(f"{'Stock':<8} {'Position':<10} {'For 10 RMB':<12} {'For 20 RMB':<12} {'For 50 RMB':<12}")

            for i, stock_info in enumerate(stocks_with_nested_position[:5]):
                code = stock_info['code']
                position = stock_info['position']

                # Calculate portfolio values for specific prices
                portfolio_for_10 = (10 * position) / 0.1
                portfolio_for_20 = (20 * position) / 0.1
                portfolio_for_50 = (50 * position) / 0.1

                print(f"{code:<8} {position:<10.2f} {portfolio_for_10:<12.0f} {portfolio_for_20:<12.0f} {portfolio_for_50:<12.0f}")

            # Analyze the technical data to see if there's a pattern in how position relates to score/angle
            print(f"\nAnalyzing relationship between position and technical indicators:")

            data_points = []
            for stock_info in stocks_with_nested_position:
                position = stock_info['position']
                tech_data = stock_info['technical_data']
                score = tech_data.get('score', 0)
                angle = tech_data.get('current_angle', 0)
                acceleration = tech_data.get('acceleration', 0)

                data_points.append({
                    'code': stock_info['code'],
                    'position': position,
                    'score': score,
                    'angle': angle,
                    'acceleration': acceleration
                })

            # Check correlation between position and other factors
            if len(data_points) > 1:
                positions = [dp['position'] for dp in data_points]
                scores = [dp['score'] for dp in data_points]
                angles = [dp['angle'] for dp in data_points]
                accelerations = [dp['acceleration'] for dp in data_points]

                # Calculate correlation coefficients
                try:
                    corr_pos_score = np.corrcoef(positions, scores)[0, 1]
                    corr_pos_angle = np.corrcoef(positions, angles)[0, 1]
                    corr_pos_accel = np.corrcoef(positions, accelerations)[0, 1]

                    print(f"\nCorrelation analysis:")
                    print(f"  Position vs Score: {corr_pos_score:.3f}")
                    print(f"  Position vs Angle: {corr_pos_angle:.3f}")
                    print(f"  Position vs Acceleration: {corr_pos_accel:.3f}")

                    # Try to determine if position is proportional to score
                    print(f"\nChecking if position is proportional to score:")
                    ratios = [pos/score for pos, score in zip(positions, scores) if score > 0]
                    if ratios:
                        avg_ratio = np.mean(ratios)
                        std_ratio = np.std(ratios)
                        print(f"  Average Position/Score ratio: {avg_ratio:.2f} ± {std_ratio:.2f}")

                except Exception as e:
                    print(f"  Error calculating correlations: {e}")

            # Show detailed technical analysis for a few stocks
            print(f"\nDetailed technical analysis for sample stocks:")
            for i, stock_info in enumerate(stocks_with_nested_position[:3]):
                code = stock_info['code']
                position = stock_info['position']
                tech_data = stock_info['technical_data']

                print(f"\n  Stock {code}:")
                print(f"    Position: {position:.2f}")
                for key, value in tech_data.items():
                    if key != 'position':
                        print(f"    {key}: {value}")

        db_manager.close_connection()
        print("\n✓ Analysis of 2025-33 positions completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analyze_2025_33_positions()
    sys.exit(0 if success else 1)

