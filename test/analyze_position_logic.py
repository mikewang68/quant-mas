#!/usr/bin/env python3
"""
Analyze the actual calculation logic for position values in the 2025-33 record
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json
import numpy as np
from scipy import stats

def analyze_position_calculation_logic():
    """Analyze the actual calculation logic for position values"""
    print("Analyzing the actual calculation logic for position values in 2025-33 record...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get the specific record 2025-33
        record = db_manager.db['pool'].find_one({'_id': '2025-33'})

        if not record:
            print("Record 2025-33 not found")
            return False

        print(f"\nRecord 2025-33:")
        print(f"  Strategy Name: {record.get('strategy_name', 'N/A')}")
        print(f"  Selection Date: {record.get('selection_date', 'N/A')}")
        print(f"  Total Stocks: {record.get('count', 'N/A')}")

        # Extract stocks with nested positions
        stocks = record.get('stocks', [])
        stocks_with_position = []

        for stock in stocks:
            tech_analysis = stock.get('tech_analysis', {})
            acc_up_trend = tech_analysis.get('acc_up_trend', {})
            if 'position' in acc_up_trend:
                stocks_with_position.append({
                    'code': stock.get('code', 'N/A'),
                    'position': acc_up_trend['position'],
                    'technical_data': acc_up_trend
                })

        print(f"\nFound {len(stocks_with_position)} stocks with position information")

        if stocks_with_position:
            print(f"\nAnalyzing position calculation logic:")

            # Collect data for analysis
            data_points = []
            for stock_info in stocks_with_position:
                position = stock_info['position']
                tech_data = stock_info['technical_data']

                data_points.append({
                    'code': stock_info['code'],
                    'position': position,
                    'score': tech_data.get('score', 0),
                    'current_angle': tech_data.get('current_angle', 0),
                    'previous_angle': tech_data.get('previous_angle', 0),
                    'acceleration': tech_data.get('acceleration', 0),
                    'signal': tech_data.get('signal', ''),
                })

            # Display statistics
            positions = [dp['position'] for dp in data_points]
            scores = [dp['score'] for dp in data_points]
            angles = [dp['current_angle'] for dp in data_points]
            accelerations = [dp['acceleration'] for dp in data_points]

            print(f"\nData statistics:")
            print(f"  Positions: min={min(positions):.2f}, max={max(positions):.2f}, mean={np.mean(positions):.2f}")
            print(f"  Scores: min={min(scores):.4f}, max={max(scores):.4f}, mean={np.mean(scores):.4f}")
            print(f"  Angles: min={min(angles):.2f}, max={max(angles):.2f}, mean={np.mean(angles):.2f}")
            print(f"  Accelerations: min={min(accelerations):.4f}, max={max(accelerations):.4f}, mean={np.mean(accelerations):.4f}")

            # Analyze correlations
            print(f"\nCorrelation analysis:")
            try:
                corr_pos_score = np.corrcoef(positions, scores)[0, 1]
                corr_pos_angle = np.corrcoef(positions, angles)[0, 1]
                corr_pos_accel = np.corrcoef(positions, accelerations)[0, 1]

                print(f"  Position vs Score: {corr_pos_score:.3f}")
                print(f"  Position vs Angle: {corr_pos_angle:.3f}")
                print(f"  Position vs Acceleration: {corr_pos_accel:.3f}")
            except Exception as e:
                print(f"  Error calculating correlations: {e}")

            # Try to determine the calculation formula
            print(f"\nAttempting to determine calculation formula:")

            # Since user mentioned it should be position ratio, let's see if these values
            # make sense as ratios (0-1 range). They don't seem to be, as they range from 10-439
            # This suggests they might be actual share counts or some other calculation

            # Let's check if there's a pattern with score
            print(f"\nAnalyzing relationship with score:")
            if len(scores) > 0 and len(positions) > 0:
                # Try linear regression: position = a * score + b
                slope, intercept, r_value, p_value, std_err = stats.linregress(scores, positions)
                print(f"  Linear fit: position = {slope:.2f} * score + {intercept:.2f}")
                print(f"  R-squared: {r_value**2:.3f}")

                # Try polynomial fit
                coeffs = np.polyfit(scores, positions, 2)
                print(f"  Quadratic fit: position = {coeffs[0]:.2f} * score² + {coeffs[1]:.2f} * score + {coeffs[2]:.2f}")

                # Try exponential relationship
                # position = a * exp(b * score)
                try:
                    log_positions = np.log(positions)
                    slope_exp, intercept_exp, r_value_exp, p_value_exp, std_err_exp = stats.linregress(scores, log_positions)
                    a_exp = np.exp(intercept_exp)
                    b_exp = slope_exp
                    print(f"  Exponential fit: position = {a_exp:.2f} * exp({b_exp:.2f} * score)")
                    print(f"  Exponential R-squared: {r_value_exp**2:.3f}")
                except:
                    print(f"  Exponential fit failed")

            # Show detailed examples
            print(f"\nDetailed examples of position calculation:")
            for i, dp in enumerate(data_points[:5]):
                print(f"\n  Stock {dp['code']}:")
                print(f"    Position: {dp['position']:.2f}")
                print(f"    Score: {dp['score']:.4f}")
                print(f"    Angle: {dp['current_angle']:.2f}")
                print(f"    Acceleration: {dp['acceleration']:.4f}")
                print(f"    Signal: {dp['signal']}")

                # Try to reverse engineer what the position might represent
                # If it's a position ratio, values like 10-439 don't make sense
                # If it's share count, we need to know portfolio value and price
                print(f"    Implied interpretation:")
                print(f"      - If position ratio: {dp['position']:.2f} (>1, unusual)")
                print(f"      - If share count with 100K portfolio: price≈{10000/dp['position']:.2f}")
                print(f"      - If share count with 1M portfolio: price≈{100000/dp['position']:.2f}")

        db_manager.close_connection()
        print("\n✓ Position calculation logic analysis completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analyze_position_calculation_logic()
    sys.exit(0 if success else 1)

