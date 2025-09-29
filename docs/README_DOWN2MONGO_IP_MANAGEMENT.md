# down2mongo.py 功能说明

## 功能概述

修改后的 `down2mongo.py` 文件增加了多项功能，用于优化股票数据获取过程并避免访问限制。

## 核心功能

### 1. 初始IP获取
- 在开始股票数据获取之前，首先获取当前IP地址
- 将初始IP添加到 `used_ip` 列表中

### 2. IP地址使用记录
- 创建了 `used_ip` 列表来记录已使用的IP地址
- 避免重复使用相同的IP地址

### 3. IP地址获取与验证
- 使用 `from utils.get_isp_ip import get_current_ip` 动态获取当前IP地址
- 在每次IP切换后验证新IP是否已在使用列表中

### 4. IP地址循环切换
- 如果获取到的IP在 `used_ip` 列表中，则重新切换IP
- 直到获取一个列表中没有的IP为止

### 5. IP地址记录更新
- 使用新IP进行股票数据获取
- 将新IP添加到 `used_ip` 列表中

### 6. 请求延时控制
- 在每只股票数据获取完成后添加1秒延时
- 降低请求频率，减少服务器压力

## 工作流程

在 `write_k_daily` 函数中：

```python
# 1. 初始化空的IP使用列表
used_ip = []

# 2. 在开始数据收集前获取初始IP
if IP_DETECTION_AVAILABLE:
    initial_ip = get_current_ip()
    if initial_ip:
        used_ip.append(initial_ip)
        print(f"Initial IP added to used list: {initial_ip}")

# 3. 在处理股票数据的循环中进行数据获取和IP管理
for code in df_code["code"]:
    # 获取股票数据
    # ... 数据获取逻辑 ...

    # 增加计数器
    stock_counter += 1
    stocks_since_last_switch += 1

    # 添加1秒延时
    time.sleep(1)

    # 每100只股票切换一次IP
    if ROUTER_CONTROL_AVAILABLE and stocks_since_last_switch >= 100:
        # 切换IP
        success = switch_ip(...)

        if success and IP_DETECTION_AVAILABLE:
            # 获取当前IP
            current_ip = get_current_ip()

            # 检查IP是否重复使用
            while current_ip in used_ip:
                # 如果在列表中，重新切换IP
                switch_ip(...)
                time.sleep(5)  # 等待IP切换完成
                current_ip = get_current_ip()

            # 将新IP添加到使用列表
            if current_ip and current_ip not in used_ip:
                used_ip.append(current_ip)
```

## 关键改进

1. **初始IP获取**：在开始数据收集前就获取并记录初始IP
2. **避免IP重复使用**：通过 `used_ip` 列表跟踪已使用的IP地址
3. **动态IP获取**：使用改进后的 `get_current_ip()` 函数获取准确的当前IP
4. **自动重试机制**：当IP重复时自动重新切换直到获取新IP
5. **访问限制防护**：通过IP轮换避免触发网站的访问限制
6. **请求频率控制**：通过1秒延时降低请求频率

## 使用说明

在股票数据获取流程中：
1. 程序启动时首先获取当前IP并加入使用列表
2. 处理每只股票后延时1秒
3. 每处理100只股票后切换IP
4. 检查新IP是否已在使用列表中
5. 如果是新IP，则用于后续数据获取
6. 将新IP添加到使用列表中

## 注意事项

1. `used_ip` 列表在程序运行期间持续增长
2. 如果所有可用IP都已使用，可能需要清空列表或等待IP释放
3. 确保 `utils.get_isp_ip.py` 文件正确配置并能获取到准确的IP地址
4. IP切换功能依赖于路由器控制模块的可用性
5. 程序中添加了5秒的等待时间，确保IP切换完成后再获取新IP
6. 初始IP获取确保程序从一开始就避免使用重复IP
7. 每只股票处理后1秒延时有助于降低服务器压力

## 代码结构

主要修改在 `write_k_daily` 函数中：
- 添加了初始IP获取逻辑
- 在数据收集开始前就初始化 `used_ip` 列表
- 实现了完整的IP管理流程
- 添加了每只股票处理后的1秒延时

