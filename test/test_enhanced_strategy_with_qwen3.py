#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test program to verify the enhanced public opinion analysis strategy works with Qwen3-4B model
This test will simulate the strategy's analyze_sentiment_with_llm method with actual Qwen3-4B responses
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, '/home/mike/quant_mas')

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2


def test_strategy_with_qwen3_response():
    """
    Test the enhanced strategy's robust extraction with actual Qwen3-4B response
    """
    print("=" * 60)
    print("Testing Enhanced Public Opinion Analysis Strategy with Qwen3-4B Response")
    print("=" * 60)

    # Create an instance of the strategy
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Simulate the problematic Qwen3-4B response content
    qwen3_response_content = '''

