# ISP IP地址检测工具使用说明

## 功能说明

`get_isp_ip.py` 是一个用于动态获取当前网络环境公网IP地址的工具。它通过访问ip138.com网站并解析iframe内容来获取准确的IP地址信息。

## 使用方法

### 1. 作为命令行工具直接运行

```bash
python utils/get_isp_ip.py
```

### 2. 从其他Python程序中调用

```python
from utils.get_isp_ip import get_current_ip

# 获取当前公网IP地址
ip_address = get_current_ip()

if ip_address:
    print(f"当前IP地址: {ip_address}")
else:
    print("无法获取IP地址")
```

### 3. 在项目中使用（需要正确设置Python路径）

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.get_isp_ip import get_current_ip

ip = get_current_ip()
```

## 函数说明

### get_current_ip()
- **功能**: 动态获取当前网络环境的公网IP地址
- **参数**: 无
- **返回值**:
  - 成功时返回字符串类型的IP地址（如 "223.102.68.134"）
  - 失败时返回 None
- **说明**: 函数会自动处理浏览器驱动、页面加载和内容解析等复杂操作

## 工作原理

1. 使用Selenium WebDriver自动打开浏览器
2. 访问ip138.com网站
3. 查找并切换到包含IP信息的iframe
4. 解析iframe中的文本内容，提取IP地址
5. 返回检测到的IP地址

## 注意事项

1. 需要安装Chrome浏览器和相关依赖
2. 首次运行时会自动下载ChromeDriver
3. 函数运行时会短暂打开浏览器窗口（无头模式下不可见）
4. 网络环境可能影响检测结果
5. 如果网站结构发生变化，可能需要更新检测逻辑

## 返回值说明

- 成功获取IP地址时，返回字符串格式的IP地址
- 无法获取时，返回 None
- 调用者应始终检查返回值是否为 None

## 示例

```python
from utils.get_isp_ip import get_current_ip

# 获取IP地址
ip = get_current_ip()

# 检查结果
if ip:
    print(f"检测到IP地址: {ip}")
    # 可以进一步处理IP地址
    # 例如：记录日志、网络配置检查等
else:
    print("未能检测到IP地址")
    # 处理异常情况
```

