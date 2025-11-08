# TP-Link路由器WAN2控制网络错误处理集成测试计划

## 测试目标
验证TP-Link路由器WAN2控制功能在网络错误条件下的稳定性和恢复能力

## 测试环境
- 系统：Quant MAS系统
- 路由器：TP-Link路由器（IP: 192.168.1.1）
- 测试脚本：`utils/enhanced_router_control.py`
- 网络错误处理：`utils/network_retry_handler.py`

## 测试场景

### 场景1：ChromeDriver初始化网络错误
**测试目的**：验证WebDriver初始化过程中的网络错误处理
**测试步骤**：
1. 模拟ChromeDriver下载失败
2. 模拟网络连接超时
3. 验证重试机制和指数退避
4. 检查系统是否优雅降级到系统PATH中的ChromeDriver

**预期结果**：
- 系统应尝试重试指定次数
- 重试间隔应遵循指数退避策略
- 最终应使用系统PATH中的ChromeDriver作为备用方案

### 场景2：路由器登录网络错误
**测试目的**：验证路由器登录过程中的网络错误处理
**测试步骤**：
1. 模拟路由器登录页面访问失败
2. 模拟登录请求超时
3. 验证网络错误检测和处理
4. 检查重试机制是否正常工作

**预期结果**：
- 网络错误应被正确识别
- 系统应触发路由器WAN2切换操作
- 重试机制应在网络恢复后继续执行

### 场景3：WAN设置页面导航错误
**测试目的**：验证WAN设置页面导航过程中的网络错误处理
**测试步骤**：
1. 模拟WAN设置页面加载失败
2. 模拟元素定位超时
3. 验证错误处理和重试机制

**预期结果**：
- 页面导航失败应触发网络错误处理
- 系统应尝试重新导航
- 重试次数应符合配置

### 场景4：WAN2接口控制错误
**测试目的**：验证WAN2接口断开/连接操作中的网络错误处理
**测试步骤**：
1. 模拟断开/连接按钮点击失败
2. 模拟操作响应超时
3. 验证网络错误检测和恢复

**预期结果**：
- 操作失败应触发网络错误处理
- 系统应尝试重新执行操作
- 最终应完成WAN2切换操作

## 测试用例

### 用例1：正常网络条件下的路由器控制
```python
# 测试正常网络条件下的完整流程
python utils/enhanced_router_control.py --router-ip 192.168.1.1 --username admin --password admin
```

### 用例2：模拟网络连接失败
```python
# 测试网络连接失败时的处理
# 需要模拟网络断开场景
```

### 用例3：模拟路由器响应超时
```python
# 测试路由器响应超时时的处理
# 需要模拟路由器响应延迟
```

### 用例4：验证重试机制
```python
# 测试重试次数和指数退避策略
# 监控重试日志和间隔时间
```

## 测试验证指标

### 功能指标
- [ ] ChromeDriver初始化成功率
- [ ] 路由器登录成功率
- [ ] WAN设置页面导航成功率
- [ ] WAN2接口控制成功率
- [ ] 网络错误检测准确率

### 性能指标
- [ ] 平均重试次数
- [ ] 重试间隔时间分布
- [ ] 总执行时间
- [ ] 错误恢复时间

### 稳定性指标
- [ ] 系统崩溃次数
- [ ] 内存泄漏情况
- [ ] 资源释放情况

## 测试工具和脚本

### 网络模拟工具
- 使用网络模拟工具创建网络延迟和丢包
- 使用防火墙规则模拟网络中断

### 监控脚本
```python
# 网络错误监控脚本
import logging
import time
from utils.enhanced_router_control import TPLinkWAN2Controller

class RouterControlMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def monitor_network_errors(self):
        """监控网络错误处理"""
        controller = TPLinkWAN2Controller()

        start_time = time.time()
        success = controller.switch_ip()
        end_time = time.time()

        execution_time = end_time - start_time

        if success:
            self.logger.info(f"路由器控制成功，执行时间: {execution_time:.2f}秒")
        else:
            self.logger.error(f"路由器控制失败，执行时间: {execution_time:.2f}秒")

        return success, execution_time
```

### 日志分析脚本
```python
# 日志分析脚本
import re

def analyze_router_logs(log_file="router_control.log"):
    """分析路由器控制日志"""
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = f.readlines()

    error_count = 0
    retry_count = 0
    network_error_count = 0

    for log in logs:
        if "错误" in log or "ERROR" in log:
            error_count += 1
        if "重试" in log or "retry" in log.lower():
            retry_count += 1
        if "网络错误" in log or "network error" in log.lower():
            network_error_count += 1

    print(f"总错误数: {error_count}")
    print(f"重试次数: {retry_count}")
    print(f"网络错误数: {network_error_count}")
```

## 测试执行计划

### 阶段1：基础功能测试
- 执行正常网络条件下的路由器控制
- 验证所有功能模块正常工作
- 建立性能基准

### 阶段2：网络错误模拟测试
- 模拟各种网络错误场景
- 验证错误检测和处理机制
- 测试重试和恢复能力

### 阶段3：稳定性测试
- 长时间运行测试
- 高频率操作测试
- 资源使用监控

### 阶段4：集成测试
- 与Quant MAS系统其他模块集成测试
- 验证数据一致性和系统稳定性

## 风险评估

### 技术风险
- 网络模拟可能影响其他系统组件
- 路由器控制失败可能导致网络中断
- 测试数据可能影响生产环境

### 缓解措施
- 在隔离环境中进行测试
- 使用测试专用的路由器
- 定期备份配置和数据

## 验收标准

### 必须满足的条件
- [ ] 网络错误检测准确率 ≥ 95%
- [ ] 错误恢复成功率 ≥ 90%
- [ ] 系统崩溃次数 = 0
- [ ] 平均执行时间 ≤ 60秒

### 期望满足的条件
- [ ] 网络错误检测准确率 ≥ 98%
- [ ] 错误恢复成功率 ≥ 95%
- [ ] 平均执行时间 ≤ 45秒
- [ ] 资源使用稳定

## 测试报告模板

### 测试执行摘要
- 测试开始时间：
- 测试结束时间：
- 测试环境：
- 测试人员：

### 测试结果统计
- 总测试用例数：
- 通过用例数：
- 失败用例数：
- 成功率：

### 详细测试结果
| 测试场景 | 状态 | 执行时间 | 错误数 | 重试次数 |
|---------|------|----------|--------|----------|
| 场景1 | ✅/❌ | XX秒 | X | X |
| 场景2 | ✅/❌ | XX秒 | X | X |
| 场景3 | ✅/❌ | XX秒 | X | X |
| 场景4 | ✅/❌ | XX秒 | X | X |

### 问题和建议
- 发现的问题：
- 改进建议：
- 风险评估：

## 附录

### 相关配置文件
- `config/router_config.json` - 路由器配置
- `utils/enhanced_router_control.py` - 路由器控制脚本
- `utils/network_retry_handler.py` - 网络错误重试处理
- `utils/network_error_handler.py` - 网络错误检测

### 参考文档
- TP-Link路由器API文档
- Selenium WebDriver文档
- Quant MAS系统架构文档

