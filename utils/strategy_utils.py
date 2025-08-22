#!/usr/bin/env python3
"""
Common utility functions for position sizing and strategy scoring
"""

import numpy as np
from typing import Union

def calculate_position_from_score(score: float) -> float:
    """
    Calculate suggested position size based on strategy score

    Args:
        score (float): Strategy score between 0 and 1

    Returns:
        float: Suggested position size as a ratio (0-1)

    Position sizing rules:
    - Score 0.8-1.0: Suggest 10-15% position
    - Score 0.6-0.8: Suggest 5-10% position
    - Score 0.4-0.6: Suggest 2-5% position
    - Score < 0.4: Suggest 0% position
    """
    # Validate input
    if not isinstance(score, (int, float)) or score < 0 or score > 1:
        raise ValueError("Score must be a number between 0 and 1")

    if score >= 0.8:
        # Linear mapping: 0.8->0.1, 1.0->0.15
        position = 0.1 + (score - 0.8) * (0.15 - 0.1) / (1.0 - 0.8)
    elif score >= 0.6:
        # Linear mapping: 0.6->0.05, 0.8->0.1
        position = 0.05 + (score - 0.6) * (0.1 - 0.05) / (0.8 - 0.6)
    elif score >= 0.4:
        # Linear mapping: 0.4->0.02, 0.6->0.05
        position = 0.02 + (score - 0.4) * (0.05 - 0.02) / (0.6 - 0.4)
    else:
        # Score < 0.4: 0% position
        position = 0.0

    # Ensure position is within bounds and round to 4 decimal places
    return round(max(0.0, min(1.0, position)), 4)

def calculate_confidence_from_metrics(sharpe_ratio: float, win_rate: float,
                                    benchmark_sharpe: float = 0.5) -> float:
    """
    Calculate strategy confidence based on performance metrics

    Args:
        sharpe_ratio (float): Strategy Sharpe ratio
        win_rate (float): Strategy win rate (0-1)
        benchmark_sharpe (float): Benchmark Sharpe ratio for comparison

    Returns:
        float: Confidence score (0-1)
    """
    # Normalize Sharpe ratio (sigmoid-like transformation)
    sharpe_confidence = 1 / (1 + np.exp(-(sharpe_ratio - benchmark_sharpe) * 2))

    # Win rate contributes to confidence (capped at 90%)
    win_rate_confidence = min(0.9, win_rate)

    # Combined confidence (weighted average)
    confidence = 0.7 * sharpe_confidence + 0.3 * win_rate_confidence

    return round(max(0.0, min(1.0, confidence)), 4)

def calculate_risk_level(volatility: float, liquidity: float, market_cap: float) -> str:
    """
    Calculate risk level based on stock characteristics

    Args:
        volatility (float): Stock volatility (ATR ratio or standard deviation)
        liquidity (float): Liquidity measure (daily volume ratio)
        market_cap (float): Market capitalization (in billions)

    Returns:
        str: Risk level ("low", "medium", "high")
    """
    # Volatility score (0-1, higher is more volatile)
    vol_score = min(1.0, volatility / 0.02)  # Assume 2% as baseline

    # Liquidity score (0-1, higher is more liquid)
    liq_score = min(1.0, liquidity / 1000000)  # Assume 1M volume as baseline

    # Market cap score (0-1, higher is lower risk)
    mc_score = 1.0 - min(1.0, market_cap / 10.0)  # Assume 10B as low risk baseline

    # Combined risk score
    risk_score = 0.4 * vol_score + 0.3 * (1 - liq_score) + 0.3 * mc_score

    if risk_score > 0.7:
        return "high"
    elif risk_score > 0.4:
        return "medium"
    else:
        return "low"

def normalize_score(raw_score: float, mean: float, std: float) -> float:
    """
    Normalize a raw score using Z-score normalization and sigmoid transformation

    Args:
        raw_score (float): Raw score value
        mean (float): Mean of score distribution
        std (float): Standard deviation of score distribution

    Returns:
        float: Normalized score between 0 and 1
    """
    if std == 0:
        return 0.5  # Neutral score if no variation

    # Z-score normalization
    z_score = (raw_score - mean) / std

    # Sigmoid transformation to bound between 0 and 1
    normalized = 1 / (1 + np.exp(-z_score))

    return round(normalized, 4)

# Example usage
if __name__ == "__main__":
    # Test position calculation
    test_scores = [0.95, 0.85, 0.75, 0.55, 0.35, 0.2]
    print("Position calculation examples:")
    for score in test_scores:
        position = calculate_position_from_score(score)
        print(f"  Score: {score:.2f} -> Position: {position*100:.2f}%")

    print("\nRisk level examples:")
    print(f"  Volatile small-cap: {calculate_risk_level(0.03, 500000, 2.0)}")
    print(f"  Stable large-cap: {calculate_risk_level(0.01, 2000000, 50.0)}")

