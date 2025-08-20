#!/usr/bin/env python3
"""
Analyze how position values are calculated in the accelerating uptrend strategy
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json

def analyze_position_calculation():
    """Analyze how position values are calculated"""
    print("Analyzing position calculation in the latest pool record...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get the latest record sorted by selection date
        latest_record = pool_collection.find_one(sort=[('selection_date', -1)])

        if not latest_record:
            print("No records found in pool collection")
            return False

        print(f"\nLatest record in pool collection:")
        print(f"  ID: {latest_record.get('_id', 'N/A')}")
        print(f"  Agent Name: {latest_record.get('agent_name', 'N/A')}")
        print(f"  Strategy Name: {latest_record.get('strategy_name', 'N/A')}")
        print(f"  Selection Date: {latest_record.get('selection_date', 'N/A')}")
        print(f"  Total Stocks: {latest_record.get('count', 'N/A')}")

        # Get stocks
        stocks = latest_record.get('stocks', [])
        print(f"\nAnalyzing {len(stocks)} stocks for position calculation...")

        # Find stocks with position information and analyze their technical analysis data
        stocks_with_position = []

        for i, stock in enumerate(stocks):
            # Look for nested position in tech_analysis.acc_up_trend
            tech_analysis = stock.get('tech_analysis', {})
            acc_up_trend = tech_analysis.get('acc_up_trend', {})
            position = acc_up_trend.get('position')

            if position is not None:
                stocks_with_position.append({
                    'index': i,
                    'code': stock.get('code', 'N/A'),
                    'position': position,
                    'technical_data': acc_up_trend
                })

        print(f"\nFound {len(stocks_with_position)} stocks with position information:")

        # Analyze the relationship between technical indicators and position calculation
        if stocks_with_position:
            print(f"\nAnalyzing position calculation logic:")
            print(f"Position appears to be calculated based on technical analysis data:")

            # Show the first stock as an example
            example_stock = stocks_with_position[0]
            print(f"\nExample - Stock {example_stock['code']}:")
            print(f"  Position: {example_stock['position']}")
            print(f"  Technical Analysis Data:")
            for key, value in example_stock['technical_data'].items():
                if key != 'position':  # Don't show position again
                    print(f"    {key}: {value}")

            # Check if there's a pattern in how position relates to other values
            print(f"\nAnalyzing position calculation pattern:")

            # Collect data for analysis
            positions = []
            scores = []
            angles = []

            for stock_info in stocks_with_position:
                positions.append(stock_info['position'])
                score = stock_info['technical_data'].get('score', 0)
                scores.append(score)
                angle = stock_info['technical_data'].get('current_angle', 0)
                angles.append(angle)

            print(f"  Position range: {min(positions):.2f} - {max(positions):.2f}")
            print(f"  Score range: {min(scores):.4f} - {max(scores):.4f}")
            print(f"  Angle range: {min(angles):.2f} - {max(angles):.2f}")

            # Try to determine the calculation formula
            # Let's check if position is proportional to score or angle
            example_stock = stocks_with_position[0]
            position = example_stock['position']
            score = example_stock['technical_data'].get('score', 0)
            angle = example_stock['technical_data'].get('current_angle', 0)
            acceleration = example_stock['technical_data'].get('acceleration', 0)

            print(f"\nAttempting to determine calculation formula using first stock:")
            print(f"  Position: {position:.6f}")
            print(f"  Score: {score:.6f}")
            print(f"  Angle: {angle:.6f}")
            print(f"  Acceleration: {acceleration:.6f}")

            # Try different formulas
            if score > 0:
                ratio_pos_to_score = position / score
                print(f"  Position/Score ratio: {ratio_pos_to_score:.2f}")

            if angle > 0:
                ratio_pos_to_angle = position / angle
                print(f"  Position/Angle ratio: {ratio_pos_to_angle:.2f}")

            if acceleration > 0:
                ratio_pos_to_accel = position / acceleration
                print(f"  Position/Acceleration ratio: {ratio_pos_to_accel:.2f}")

            # Check if it might be based on a combination of factors
            # Try position = score * angle * some_factor
            if score > 0 and angle > 0:
                combined_factor = position / (score * angle)
                print(f"  Position/(Score*Angle) factor: {combined_factor:.2f}")

        # Check if there are stocks without nested position but with top-level position
        stocks_with_top_level_position = [s for s in stocks if 'position' in s and 'tech_analysis' not in s]
        if stocks_with_top_level_position:
            print(f"\nFound {len(stocks_with_top_level_position)} stocks with top-level position field")
        else:
            print(f"\nNo stocks found with top-level position field")

        db_manager.close_connection()
        print("\n✓ Position calculation analysis completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analyze_position_calculation()
    sys.exit(0 if success else 1)

