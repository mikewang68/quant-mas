# TP-Link路由器右侧WAN2控制器

这是一个专门用于控制TP-Link路由器右侧WAN2接口的Python脚本。

## 问题说明

之前的脚本可能错误地操作了左侧的WAN1接口而不是右侧的WAN2接口。此修正版本通过元素位置判断来确保操作右侧的WAN2接口。

## 功能特点

1. **右侧WAN2专用**: 通过元素位置判断确保操作右侧WAN2接口
2. **自动浏览器控制**: 使用Selenium自动控制Chrome浏览器
3. **灵活配置**: 支持命令行参数和配置文件两种方式配置路由器信息
4. **增强稳定性**: 多种元素定位策略，提高脚本稳定性
5. **详细日志**: 完整的操作日志记录
6. **错误处理**: 完善的异常处理机制

## 安装依赖

```bash
pip install selenium webdriver-manager
```

## 使用方法

### 1. 基本使用（使用配置文件）

```bash
python right_side_wan2_controller.py --config router_config.json
```

### 2. 命令行参数方式

```bash
python right_side_wan2_controller.py --router-ip 192.168.1.1 --username your_username --password your_password
```

### 3. 不使用headless模式（用于调试）

```bash
python right_side_wan2_controller.py --config router_config.json --no-headless
```

### 4. 自定义等待时间

```bash
python right_side_wan2_controller.py --config router_config.json --wait-time 5
```

## 配置文件格式

创建一个JSON格式的配置文件（如router_config.json）：

```json
{
    "router_ip": "192.168.1.1",
    "username": "your_username",
    "password": "your_password"
}
```

## 命令行参数说明

- `--config`: 配置文件路径
- `--router-ip`: 路由器IP地址
- `--username`: 路由器用户名
- `--password`: 路由器密码
- `--wait-time`: 等待时间（秒），默认为3秒
- `--no-headless`: 不使用headless模式运行浏览器

## 工作原理

此脚本通过以下方式确保操作右侧WAN2接口：

1. **导航到WAN设置页面**: 自动登录并导航到WAN设置页面
2. **识别右侧按钮**: 通过元素的x坐标位置判断，确保操作右侧的WAN2接口
3. **执行操作**: 对右侧WAN2的断开和连接按钮执行相应操作

## 日志文件

脚本会生成日志文件 `right_wan2_control.log`，记录详细的操作过程和错误信息。

## 注意事项

1. 确保路由器可以正常通过浏览器访问
2. 确保用户名和密码正确
3. 脚本会自动下载ChromeDriver，需要网络连接
4. 如果路由器界面有变化，可能需要调整元素定位策略

## 故障排除

1. **元素定位失败**: 检查路由器界面是否有变化，可能需要更新元素定位策略
2. **登录失败**: 检查用户名和密码是否正确
3. **浏览器驱动问题**: 确保网络连接正常，可以访问ChromeDriver下载地址
4. **权限问题**: 确保脚本有足够的权限运行

