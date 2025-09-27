#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate LLM strategy scoring logic
"""

import sys
import os
import json
import re

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy


def test_score_extraction():
    """Test score extraction from various content formats"""
    print("Testing score extraction from different content formats...")

    # Test case 1: Content with score in text
    content1 = "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。"
    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', content1, re.IGNORECASE)
    if score_matches:
        extracted_score = float(score_matches[0])
        # Normalize if in 0-100 range
        if 0 <= extracted_score <= 100:
            normalized_score = max(0.0, min(1.0, extracted_score / 100.0))
        else:
            normalized_score = extracted_score
        print(f"✓ Content 1 - Extracted score: {extracted_score}, Normalized: {normalized_score}")
    else:
        print("✗ Content 1 - No score found, would use default: 0.0")

    # Test case 2: Content with 0-100 range score
    content2 = "综合考虑以上因素，我给出的基本面评分是85。这个评分反映了公司在行业中具有较强的竞争优势。"
    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', content2, re.IGNORECASE)
    if score_matches:
        extracted_score = float(score_matches[0])
        # Normalize if in 0-100 range
        if 0 <= extracted_score <= 100:
            normalized_score = max(0.0, min(1.0, extracted_score / 100.0))
        else:
            normalized_score = extracted_score
        print(f"✓ Content 2 - Extracted score: {extracted_score}, Normalized: {normalized_score}")
    else:
        print("✗ Content 2 - No score found, would use default: 0.0")

    # Test case 3: Content without explicit score
    content3 = "综合考虑以上因素，该公司基本面表现良好，具有较强的竞争优势和稳定的盈利能力。"
    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', content3, re.IGNORECASE)
    if score_matches:
        extracted_score = float(score_matches[0])
        # Normalize if in 0-100 range
        if 0 <= extracted_score <= 100:
            normalized_score = max(0.0, min(1.0, extracted_score / 100.0))
        else:
            normalized_score = extracted_score
        print(f"✓ Content 3 - Extracted score: {extracted_score}, Normalized: {normalized_score}")
    else:
        print("✗ Content 3 - No score found, would use default: 0.0")

    print()


def test_value_extraction():
    """Test value/analysis text extraction from content"""
    print("Testing value/analysis text extraction...")

    # Test case 1: Content with score followed by analysis
    content1 = "综合考虑以上因素，我给出的基本面评分是0.65。这个评分反映了公司在盈利能力方面表现良好，但在营收增长方面存在不足。公司具有稳定的盈利能力和良好的行业地位，但需要关注其资产负债率的上升趋势。"

    value_patterns = [
        r'综合考虑以上因素，我给出的基本面评分是[\d.]+。(.*)',
        r'综合考虑以上因素，我给出的基本面评分是[\d.]+。这个评分反映了.*?不足。(.*?)(?:\n\n|$)',
        r'综合考虑以上因素，我给出的基本面评分是[\d.]+。这个评分反映了.*?不足。(.*)$',
    ]

    extracted_value = content1  # Default to full content
    for pattern in value_patterns:
        match = re.search(pattern, content1, re.DOTALL | re.IGNORECASE)
        if match:
            extracted_value = match.group(1).strip()
            if extracted_value:
                break

    print(f"✓ Content 1 - Extracted value: {extracted_value}")
    print()


def test_json_parsing_fallback():
    """Test the fallback logic when JSON parsing fails"""
    print("Testing JSON parsing fallback logic...")

    # Simulate raw content that would fail JSON parsing but contains score info
    raw_content = "综合考虑以上因素，我给出的基本面评分是0.75。这个评分反映了公司在行业中具有较强的竞争优势。"

    # This is what the current implementation does:
    llm_score = 0.0  # Default score (not 50.0)
    llm_value = raw_content

    # Try to extract score from raw content using regex
    score_matches = re.findall(r'(?:评分|score)[:：]?\s*(\d+\.?\d*)', raw_content, re.IGNORECASE)
    if score_matches:
        try:
            extracted_score = float(score_matches[0])
            # If score is in 0-100 range, normalize to 0-1 range
            if 0 <= extracted_score <= 100:
                llm_score = max(0.0, min(1.0, extracted_score / 100.0))
            elif 0 <= extracted_score <= 1:
                llm_score = extracted_score
        except ValueError:
            pass  # If we can't parse the extracted score, keep default

    print(f"✓ Fallback logic result - Score: {llm_score}, Value: {llm_value[:50]}...")
    print()


def demonstrate_why_zero_is_better_than_fifty():
    """Demonstrate why using 0.0 as default is better than 50.0"""
    print("Why 0.0 is better than 50.0 as default score:")
    print("1. 0.0 represents 'no information' or 'analysis failed'")
    print("2. 50.0 represents 'neutral' which implies some level of confidence")
    print("3. When JSON parsing fails, we don't want to mislead the system")
    print("4. A score of 0.0 will be properly filtered out by selection algorithms")
    print("5. 0.0 makes it clear that the analysis was not successful")
    print()


def main():
    """Run all tests"""
    print("LLM Strategy Scoring Logic Tests\n")

    test_score_extraction()
    test_value_extraction()
    test_json_parsing_fallback()
    demonstrate_why_zero_is_better_than_fifty()

    print("All tests completed!")


if __name__ == "__main__":
    main()

