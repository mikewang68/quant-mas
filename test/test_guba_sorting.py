"""
测试东方财富股吧数据倒排序功能
"""

import sys
sys.path.append('.')

from utils.eastmoney_guba_scraper import EastMoneyGubaScraper

# 测试数据 - 模拟不同时间的帖子
test_posts = [
    {"read_count": "100", "comment_count": "10", "title": "帖子1", "author": "作者1", "last_update": "09-25 10:00"},
    {"read_count": "200", "comment_count": "20", "title": "帖子2", "author": "作者2", "last_update": "09-30 15:30"},
    {"read_count": "150", "comment_count": "15", "title": "帖子3", "author": "作者3", "last_update": "09-28 08:45"},
    {"read_count": "300", "comment_count": "30", "title": "帖子4", "author": "作者4", "last_update": "09-29 14:20"},
    {"read_count": "250", "comment_count": "25", "title": "帖子5", "author": "作者5", "last_update": "09-27 11:10"},
]

def test_sorting():
    print("=== 测试倒排序功能 ===")

    # 测试时间解析函数
    print("\n1. 测试时间解析函数:")
    test_times = ["09-25 10:00", "09-30 15:30", "09-28 08:45", "09-29 14:20", "09-27 11:10"]
    for time_str in test_times:
        parsed_time = EastMoneyGubaScraper._parse_time(time_str)
        print(f"  原始时间: {time_str} -> 解析后: {parsed_time}")

    # 测试排序功能
    print("\n2. 测试排序功能:")
    print("   原始数据顺序:")
    for i, post in enumerate(test_posts, 1):
        print(f"     {i}. {post['last_update']}: {post['title']}")

    # 进行倒排序
    sorted_posts = sorted(test_posts, key=lambda x: EastMoneyGubaScraper._parse_time(x.get('last_update', '')), reverse=True)

    print("\n   倒排序后顺序:")
    for i, post in enumerate(sorted_posts, 1):
        print(f"     {i}. {post['last_update']}: {post['title']}")

    # 验证排序是否正确
    expected_order = ["09-30 15:30", "09-29 14:20", "09-28 08:45", "09-27 11:10", "09-25 10:00"]
    actual_order = [post['last_update'] for post in sorted_posts]

    if actual_order == expected_order:
        print("\n✅ 排序功能正常: 数据按时间倒序排列正确")
    else:
        print(f"\n❌ 排序功能异常:")
        print(f"   期望顺序: {expected_order}")
        print(f"   实际顺序: {actual_order}")

    # 测试取前3条
    print("\n3. 测试取前3条:")
    top_3_posts = sorted_posts[:3]
    for i, post in enumerate(top_3_posts, 1):
        print(f"     {i}. {post['last_update']}: {post['title']}")

    if len(top_3_posts) == 3:
        print("✅ 取前N条功能正常")
    else:
        print("❌ 取前N条功能异常")

if __name__ == "__main__":
    test_sorting()

