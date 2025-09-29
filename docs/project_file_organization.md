# 项目文件整理记录

## 概述
本文档记录了对项目文件结构的整理工作，目的是使项目目录结构更加清晰，便于维护和问题排查。

## 整理时间
2025年9月29日

## 整理前状况
`utils` 目录下文件混杂，包含：
- 正式运行的功能性程序
- 测试程序和调试脚本
- 文档和说明文件

总计超过150个文件，查找和维护困难。

## 整理后结构

### 1. utils 目录（功能性程序）
保留了核心的功能性程序，包括：

1. `down2mongo.py` - 主要的数据下载程序
2. `run_public_opinion_selector.py` - 运行公共舆情选择器
3. `run_weekly_selector.py` - 运行周选择器
4. `run_fundamental_selector.py` - 运行基本面选择器
5. `enhanced_router_control.py` - 增强的路由器控制
6. `get_isp_ip.py` - 获取ISP IP地址
7. `akshare_client.py` - Akshare数据客户端
8. `logger.py` - 日志记录工具
9. `paths.py` - 路径管理工具
10. `strategy_utils.py` - 策略工具函数
11. `position_calculator.py` - 仓位计算器
12. `program_manager.py` - 程序管理器
13. `strategy_result_formatter.py` - 策略结果格式化器

### 2. test 目录（测试和调试程序）
将约130个测试和调试程序移动到 `test` 目录，包括：
- 各种测试脚本
- 调试工具
- 示例程序
- 实验性代码

### 3. docs 目录（文档）
将7个文档文件移动到 `docs` 目录，包括：
- `DEMO_INSTRUCTIONS.md` - 演示说明
- `README_right_side_wan2.md` - 右侧WAN2说明
- `README_DOWN2MONGO_IP_MANAGEMENT.md` - IP管理说明
- `README_right_wan2_control.md` - WAN2控制说明
- `README_IP_DETECTION.md` - IP检测说明
- `README_right_wan2_restart.md` - WAN2重启说明
- `README_router_control.md` - 路由器控制说明

## 整理效果
1. **提高可维护性** - 功能性程序集中在utils目录，便于查找和维护
2. **清晰的文件分类** - 测试、文档和功能代码分离，结构清晰
3. **便于问题排查** - 开发者可以快速定位到相关文件
4. **减少混乱** - 避免在功能性目录中混杂测试和文档文件

## 后续建议
1. 为新添加的工具程序建立明确的分类规则
2. 定期清理不再使用的测试文件
3. 维护此文档，记录后续的文件结构调整

