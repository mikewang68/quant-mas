#!/usr/bin/env python3
"""
Investigate how position values are calculated by examining the actual calculation logic
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json
import numpy as np

def reverse_engineer_position_calculation():
    """Reverse engineer how position values are calculated"""
    print("Reverse engineering position calculation in the latest pool record...")

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

        # Reverse engineer the calculation formula
        if stocks_with_position:
            print(f"\nReverse engineering position calculation formula:")

            # Collect data for analysis
            data_points = []
            for stock_info in stocks_with_position:
                position = stock_info['position']
                score = stock_info['technical_data'].get('score', 0)
                angle = stock_info['technical_data'].get('current_angle', 0)
                acceleration = stock_info['technical_data'].get('acceleration', 0)

                data_points.append({
                    'code': stock_info['code'],
                    'position': position,
                    'score': score,
                    'angle': angle,
                    'acceleration': acceleration
                })

            # Try various formulas to see which one fits best
            print(f"\nTesting different position calculation formulas:")

            # Formula 1: position = score * angle * constant
            print(f"Formula 1: position = score * angle * constant")
            constants_1 = []
            for dp in data_points:
                if dp['score'] > 0 and dp['angle'] > 0:
                    constant = dp['position'] / (dp['score'] * dp['angle'])
                    constants_1.append(constant)

            if constants_1:
                avg_constant_1 = np.mean(constants_1)
                std_constant_1 = np.std(constants_1)
                print(f"  Average constant: {avg_constant_1:.2f} ± {std_constant_1:.2f}")

                # Test accuracy of this formula
                errors_1 = []
                for dp in data_points[:10]:  # Test with first 10 stocks
                    calculated = dp['score'] * dp['angle'] * avg_constant_1
                    actual = dp['position']
                    error = abs(calculated - actual) / actual * 100  # Percentage error
                    errors_1.append(error)

                avg_error_1 = np.mean(errors_1)
                print(f"  Average error: {avg_error_1:.2f}%")

            # Formula 2: position = score * acceleration * constant
            print(f"\nFormula 2: position = score * acceleration * constant")
            constants_2 = []
            for dp in data_points:
                if dp['score'] > 0 and dp['acceleration'] != 0:
                    constant = dp['position'] / (dp['score'] * dp['acceleration'])
                    constants_2.append(constant)

            if constants_2:
                avg_constant_2 = np.mean(constants_2)
                std_constant_2 = np.std(constants_2)
                print(f"  Average constant: {avg_constant_2:.2f} ± {std_constant_2:.2f}")

                # Test accuracy of this formula
                errors_2 = []
                for dp in data_points[:10]:  # Test with first 10 stocks
                    calculated = dp['score'] * dp['acceleration'] * avg_constant_2
                    actual = dp['position']
                    error = abs(calculated - actual) / actual * 100  # Percentage error
                    errors_2.append(error)

                avg_error_2 = np.mean(errors_2)
                print(f"  Average error: {avg_error_2:.2f}%")

            # Formula 3: position = (score * angle * acceleration) * constant
            print(f"\nFormula 3: position = (score * angle * acceleration) * constant")
            constants_3 = []
            for dp in data_points:
                if dp['score'] > 0 and dp['angle'] > 0 and dp['acceleration'] != 0:
                    constant = dp['position'] / (dp['score'] * dp['angle'] * dp['acceleration'])
                    constants_3.append(constant)

            if constants_3:
                avg_constant_3 = np.mean(constants_3)
                std_constant_3 = np.std(constants_3)
                print(f"  Average constant: {avg_constant_3:.2f} ± {std_constant_3:.2f}")

                # Test accuracy of this formula
                errors_3 = []
                for dp in data_points[:10]:  # Test with first 10 stocks
                    calculated = dp['score'] * dp['angle'] * dp['acceleration'] * avg_constant_3
                    actual = dp['position']
                    error = abs(calculated - actual) / actual * 100  # Percentage error
                    errors_3.append(error)

                avg_error_3 = np.mean(errors_3)
                print(f"  Average error: {avg_error_3:.2f}%")

            # Formula 4: position = score * constant (simple)
            print(f"\nFormula 4: position = score * constant")
            constants_4 = []
            for dp in data_points:
                if dp['score'] > 0:
                    constant = dp['position'] / dp['score']
                    constants_4.append(constant)

            if constants_4:
                avg_constant_4 = np.mean(constants_4)
                std_constant_4 = np.std(constants_4)
                print(f"  Average constant: {avg_constant_4:.2f} ± {std_constant_4:.2f}")

                # Test accuracy of this formula
                errors_4 = []
                for dp in data_points[:10]:  # Test with first 10 stocks
                    calculated = dp['score'] * avg_constant_4
                    actual = dp['position']
                    error = abs(calculated - actual) / actual * 100  # Percentage error
                    errors_4.append(error)

                avg_error_4 = np.mean(errors_4)
                print(f"  Average error: {avg_error_4:.2f}%")

            # Formula 5: position = angle * constant (simple)
            print(f"\nFormula 5: position = angle * constant")
            constants_5 = []
            for dp in data_points:
                if dp['angle'] > 0:
                    constant = dp['position'] / dp['angle']
                    constants_5.append(constant)

            if constants_5:
                avg_constant_5 = np.mean(constants_5)
                std_constant_5 = np.std(constants_5)
                print(f"  Average constant: {avg_constant_5:.2f} ± {std_constant_5:.2f}")

                # Test accuracy of this formula
                errors_5 = []
                for dp in data_points[:10]:  # Test with first 10 stocks
                    calculated = dp['angle'] * avg_constant_5
                    actual = dp['position']
                    error = abs(calculated - actual) / actual * 100  # Percentage error
                    errors_5.append(error)

                avg_error_5 = np.mean(errors_5)
                print(f"  Average error: {avg_error_5:.2f}%")

            # Show the most accurate formula
            print(f"\nMost accurate formula:")
            errors = [
                (avg_error_1, "score * angle * constant"),
                (avg_error_2, "score * acceleration * constant"),
                (avg_error_3, "(score * angle * acceleration) * constant"),
                (avg_error_4, "score * constant"),
                (avg_error_5, "angle * constant")
            ]

            # Filter out None errors
            valid_errors = [(error, name) for error, name in errors if not np.isnan(error)]

            if valid_errors:
                best_formula = min(valid_errors, key=lambda x: x[0])
                print(f"  {best_formula[1]} with {best_formula[0]:.2f}% average error")

        db_manager.close_connection()
        print("\n✓ Position calculation reverse engineering completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = reverse_engineer_position_calculation()
    sys.exit(0 if success else 1)

