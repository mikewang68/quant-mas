#!/usr/bin/env python3
"""
Position Calculator Utility
Calculate position sizes based on strategy scores for consistent risk management across all strategies.
"""

def calculate_position_from_score(score):
    """
    Calculate suggested position size based on strategy score.

    This function provides a standardized way to convert strategy scores to position sizes
    across all strategies in the system.

    Args:
        score (float): Strategy score between 0 and 1

    Returns:
        float: Suggested position size as a ratio (0-1)
               Returns 0 for scores below 0.4

    Position sizing rules:
    - Score 0.8-1.0: Suggest 10-15% position
    - Score 0.6-0.8: Suggest 5-10% position
    - Score 0.4-0.6: Suggest 2-5% position
    - Score < 0.4: Suggest 0% position

    Examples:
        >>> calculate_position_from_score(0.9)
        0.125
        >>> calculate_position_from_score(0.7)
        0.075
        >>> calculate_position_from_score(0.5)
        0.035
        >>> calculate_position_from_score(0.3)
        0.0
    """
    # Input validation
    if not isinstance(score, (int, float)):
        raise TypeError("Score must be a number")

    if score < 0 or score > 1:
        raise ValueError("Score must be between 0 and 1")

    # Calculate position based on score ranges
    if score >= 0.8:
        # Score 0.8-1.0: Suggest 10-15% position
        # Linear interpolation: 0.8->0.1, 1.0->0.15
        position = 0.1 + (score - 0.8) * (0.15 - 0.1) / (1.0 - 0.8)
    elif score >= 0.6:
        # Score 0.6-0.8: Suggest 5-10% position
        # Linear interpolation: 0.6->0.05, 0.8->0.1
        position = 0.05 + (score - 0.6) * (0.1 - 0.05) / (0.8 - 0.6)
    elif score >= 0.4:
        # Score 0.4-0.6: Suggest 2-5% position
        # Linear interpolation: 0.4->0.02, 0.6->0.05
        position = 0.02 + (score - 0.4) * (0.05 - 0.02) / (0.6 - 0.4)
    else:
        # Score < 0.4: Suggest 0% position
        position = 0.0

    # Ensure result is within bounds and round to reasonable precision
    return round(max(0.0, min(1.0, position)), 4)


def score_to_position_mapping():
    """
    Return the score to position mapping rules for reference.

    Returns:
        dict: Mapping of score ranges to position size ranges
    """
    return {
        "0.8-1.0": "10-15% position",
        "0.6-0.8": "5-10% position",
        "0.4-0.6": "2-5% position",
        "0.0-0.4": "0% position"
    }


# Example usage and testing
if __name__ == "__main__":
    # Test the function with various scores
    test_scores = [0.95, 0.85, 0.75, 0.55, 0.45, 0.35, 0.2, 0.0]

    print("Score to Position Mapping:")
    print("=" * 30)
    for score_range, position_range in score_to_position_mapping().items():
        print(f"  Score {score_range}: {position_range}")

    print("\nTest Results:")
    print("=" * 30)
    for score in test_scores:
        position = calculate_position_from_score(score)
        print(f"  Score: {score:4.2f} -> Position: {position*100:5.2f}%")

