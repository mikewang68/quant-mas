#!/usr/bin/env python3
"""
验证K线图tooltip修复脚本
"""

import re

def verify_kline_fix():
    """验证K线图tooltip修复是否正确应用"""

    with open('web/templates/stock_kline_v2.html', 'r', encoding='utf-8') as f:
        content = f.read()

    print("=== K线图tooltip修复验证 ===")

    # 检查数据构建部分
    data_build_pattern = r'const ohlcData = pageData\.map\(item => \[\s*item\.open,\s*item\.high,\s*item\.low,\s*item\.close\s*\]\)'
    data_build_match = re.search(data_build_pattern, content, re.DOTALL)

    if data_build_match:
        print("✅ 数据构建顺序正确: [open, high, low, close]")
    else:
        print("❌ 数据构建顺序错误")
        # 查找实际的数据构建代码
        actual_build = re.search(r'const ohlcData = pageData\.map\(item => \[[^\]]+\]\)', content, re.DOTALL)
        if actual_build:
            print(f"   实际代码: {actual_build.group(0)[:100]}...")

    # 检查tooltip显示部分
    tooltip_pattern = r'开: \$\{data\[0\]\.toFixed\(2\)\}.*?高: \$\{data\[1\]\.toFixed\(2\)\}.*?低: \$\{data\[2\]\.toFixed\(2\)\}.*?收: \$\{data\[3\]\.toFixed\(2\)\}'
    tooltip_match = re.search(tooltip_pattern, content, re.DOTALL)

    if tooltip_match:
        print("✅ Tooltip显示顺序正确: 开→高→低→收")
    else:
        print("❌ Tooltip显示顺序错误")
        # 查找实际的tooltip代码
        actual_tooltip = re.search(r'开:.*?收:', content, re.DOTALL)
        if actual_tooltip:
            print(f"   实际代码: {actual_tooltip.group(0)[:100]}...")

    print("\n=== 修复状态总结 ===")
    if data_build_match and tooltip_match:
        print("✅ 所有修复已正确应用")
        print("\n如果用户仍然看到问题，可能是：")
        print("1. 浏览器缓存 - 请按Ctrl+F5强制刷新")
        print("2. Web服务需要重启")
        print("3. 检查网络面板确认API返回的数据格式")
    else:
        print("❌ 修复未完全应用，请重新检查代码")

if __name__ == "__main__":
    verify_kline_fix()

