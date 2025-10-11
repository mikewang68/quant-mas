#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test program to verify enhanced extraction methods for Qwen3-4B model responses
This test will help us understand if our improved extraction methods work correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
import json
import re


def test_robust_extraction():
    """Test the robust extraction methods with actual Qwen3-4B responses"""

    # Sample response from Qwen3-4B that includes thinking process
    sample_response = '''

