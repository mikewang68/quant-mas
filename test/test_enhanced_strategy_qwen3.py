#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test program to verify the enhanced public opinion analysis strategy works with Qwen3-4B model
This test will simulate the strategy's sentiment analysis with the actual LLM response format
"""

import sys
import os
import json
import re
from typing import Optional

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def extract_sentiment_score_robust(content: str) -> Optional[float]:
    """
    Robustly extract sentiment score from content using multiple methods
    This is a copy of the method from the enhanced public opinion analysis strategy
    """
    try:
        # Method 1: Handle case where JSON is embedded within thinking process
        # Look for the JSON object that contains sentiment_score
        # First, try to find a complete JSON object
        json_start = content.find('{')
        json_end = content.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            # Extract potential JSON content
            json_content = content[json_start:json_end+1]
            try:
                # Try to parse the extracted JSON content
                analysis_result = json.loads(json_content)
                if "sentiment_score" in analysis_result:
                    sentiment_score = float(analysis_result["sentiment_score"])
                    return max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1 range
            except json.JSONDecodeError:
                # If JSON parsing fails, continue with other methods
                pass

        # Method 2: Try to find JSON object that contains sentiment_score using regex
        # This handles cases where there might be multiple JSON objects
        json_matches = re.findall(r'\{[^{}]*"sentiment_score"[^{}]*\}', content)
        for json_match in json_matches:
            try:
                analysis_result = json.loads(json_match)
                if "sentiment_score" in analysis_result:
                    sentiment_score = float(analysis_result["sentiment_score"])
                    return max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1 range
            except json.JSONDecodeError:
                continue

        # Method 3: Try standard regex pattern
        # Pattern 1: Standard format
        score_match = re.search(r'"sentiment_score"\s*:\s*(\d+\.?\d*)', content)
        if score_match:
            sentiment_score = float(score_match.group(1))
            return max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1 range

        # Pattern 2: Alternative format with different quotes
        score_match = re.search(r"'sentiment_score'\s*:\s*(\d+\.?\d*)", content)
        if score_match:
            sentiment_score = float(score_match.group(1))
            return max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1 range

        # Pattern 3: Find any number that looks like a sentiment score (between 0 and 1)
        number_matches = re.findall(r'(\d+\.?\d*)', content)
        for match in number_matches:
            try:
                score = float(match)
                # Check if it's in valid range and has reasonable decimal places
                if 0 <= score <= 1 and len(match.split('.')[-1]) <= 2:
                    return score
            except ValueError:
                continue

        # Pattern 4: Handle cases where score might be labeled differently
        # Look for patterns like "score: 0.75" or "评分: 0.75"
        score_patterns = [
            r'[Ss]core\s*[:：]\s*(\d+\.?\d*)',
            r'[Ss]entiment\s*[:：]\s*(\d+\.?\d*)',
            r'[评评分]\s*[:：]\s*(\d+\.?\d*)',
            r'[一-龥]*[Ss]core[一-龥]*\s*[:：]\s*(\d+\.?\d*)'
        ]

        for pattern in score_patterns:
            score_match = re.search(pattern, content)
            if score_match:
                sentiment_score = float(score_match.group(1))
                return max(0.0, min(1.0, sentiment_score))  # Clamp to 0-1 range

        return None

    except Exception as e:
        print(f"Error in robust sentiment score extraction: {e}")
        return None

def test_with_actual_llm_response():
    """
    Test with actual LLM response from Qwen3-4B model
    """
    # This is the actual response we got from the Qwen3-4B model
    llm_response = '''

