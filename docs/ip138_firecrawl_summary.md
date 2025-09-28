# 使用Firecrawl获取ip138.com IP地址总结报告

## 项目目标
使用Firecrawl爬取https://www.ip138.com/中的IP地址

## 实施过程

### 1. 初步尝试：直接访问主页
- **结果**：未找到IP地址
- **原因**：
  - ip138.com主页通过iframe显示IP地址
  - Firecrawl抓取的主页内容不包含实际的IP信息
  - IP地址信息在iframe中动态加载

### 2. 深入分析：检查页面结构
通过分析Firecrawl返回的HTML内容，发现关键信息：
```html
<iframe src="//2025.ip138.com/" rel="nofollow" width="100%" height="80" frameborder="0" scrolling="no"></iframe>
```

### 3. 直接访问iframe：成功获取IP地址
- **目标URL**：https://2025.ip138.com/
- **结果**：成功获取到IP地址 `119.109.53.250`
- **附加信息**：地理位置为中国辽宁大连 联通

## 技术分析

### 为什么能成功获取
1. **服务器端渲染**：ip138.com的iframe内容是服务器端渲染的
2. **静态内容**：IP地址直接嵌入在HTML中，不需要JavaScript执行
3. **Firecrawl能力**：能够抓取服务器端渲染的静态内容

### 与WebRTC地址的区别
| 特性 | ip138.com IP地址 | WebRTC地址 |
|------|------------------|------------|
| 加载方式 | 服务器端渲染 | JavaScript动态获取 |
| Firecrawl支持 | ✅ 可以获取 | ❌ 无法获取 |
| 需要浏览器 | ❌ 不需要 | ✅ 必须需要 |
| 实时性 | 请求时生成 | 实时获取 |

## 实现文件

### 核心脚本
- `get_ip138_iframe.py` - 直接获取iframe中IP地址的脚本

### 关键代码
```python
# 直接访问显示IP的iframe
target_url = "https://2025.ip138.com/"

# 使用Firecrawl抓取
payload = {
    "url": target_url,
    "formats": ["markdown", "html"]
}

# 提取IP地址
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv4_addresses = re.findall(ipv4_pattern, content)
```

## 获取结果

### 成功获取的IP地址
- **IP地址**：`119.109.53.250`
- **地理位置**：中国辽宁大连 联通
- **来源**：Firecrawl服务器的公网IP地址

### 重要说明
通过Firecrawl获取的是Firecrawl服务器的IP地址，而不是用户本地的IP地址。这与直接访问网站看到的IP地址是不同的。

## 使用方法

### 运行脚本
```bash
python get_ip138_iframe.py
```

### 预期输出
```
=== 最终结果 ===
获取到的IPv4地址:
  - 119.109.53.250
```

## 应用场景

### 适用情况
1. **获取Firecrawl服务器IP**：了解爬虫服务器的公网IP
2. **代理检测**：检查Firecrawl是否使用代理
3. **地理位置分析**：分析爬虫服务器的地理位置
4. **网络环境测试**：测试Firecrawl的网络环境

### 不适用情况
1. **获取用户本地IP**：无法获取访问者的真实IP地址
2. **实时IP监控**：Firecrawl服务器IP相对固定
3. **WebRTC本地IP**：无法获取局域网IP地址

## 结论

成功实现了使用Firecrawl获取ip138.com网站IP地址的目标。关键在于：

1. **正确识别目标页面**：找到实际显示IP地址的iframe页面
2. **理解技术原理**：区分服务器端渲染和客户端动态加载
3. **合理使用工具**：充分发挥Firecrawl在静态内容抓取方面的优势

与之前尝试获取WebRTC地址不同，ip138.com的IP地址可以通过Firecrawl成功获取，这为类似需求提供了有效的解决方案。

