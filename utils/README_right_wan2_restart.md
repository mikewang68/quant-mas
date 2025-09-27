# TP-Link路由器右侧WAN2重启录制脚本

这是一个专门用于重启TP-Link路由器右侧WAN2接口并录制操作过程的Python脚本。

## 功能特点

1. **右侧WAN2专用**: 通过元素位置判断确保操作右侧WAN2接口
2. **自动浏览器控制**: 使用Selenium自动控制Chrome浏览器
3. **重启功能**: 自动断开并重新连接右侧WAN2
4. **录制支持**: 支持操作过程录制（需要额外工具）
5. **灵活配置**: 支持命令行参数和配置文件两种方式配置路由器信息
6. **详细日志**: 完整的操作日志记录
7. **错误处理**: 完善的异常处理机制

## 安装依赖

```bash
pip install selenium webdriver-manager
```

## 使用方法

### 1. 基本使用（使用配置文件）

```bash
python right_wan2_restart_recorder.py --config router_config.json
```

### 2. 命令行参数方式

```bash
python right_wan2_restart_recorder.py --router-ip 192.168.1.1 --username your_username --password your_password
```

### 3. 使用headless模式

```bash
python right_wan2_restart_recorder.py --config router_config.json --headless
```

### 4. 启用录制功能

```bash
python right_wan2_restart_recorder.py --config router_config.json --record
```

### 5. 自定义等待时间

```bash
python right_wan2_restart_recorder.py --config router_config.json --wait-time 5
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
- `--headless`: 使用headless模式运行浏览器（无界面）
- `--record`: 启用录制功能（需要额外的录制工具）

## 工作原理

此脚本通过以下方式确保操作右侧WAN2接口：

1. **导航到WAN设置页面**: 自动登录并导航到WAN设置页面
2. **识别右侧按钮**: 通过元素的x坐标位置判断，确保操作右侧的WAN2接口
3. **执行重启**: 先断开右侧WAN2连接，等待一段时间后重新连接
4. **录制过程**: 如果启用录制功能，会记录整个操作过程

## 日志文件

脚本会生成日志文件 `right_wan2_recording.log`，记录详细的操作过程和错误信息。

## 录制功能说明

当前版本的脚本设置了浏览器录制相关的选项，但实际的屏幕录制需要额外的工具支持：

1. **Windows**: 可以使用OBS Studio等工具录制
2. **Linux**: 可以使用FFmpeg或OBS Studio录制
3. **Mac**: 可以使用QuickTime Player或OBS Studio录制

## 注意事项

1. 确保路由器可以正常通过浏览器访问
2. 确保用户名和密码正确
3. 脚本会自动下载ChromeDriver，需要网络连接
4. 如果路由器界面有变化，可能需要调整元素定位策略
5. 录制功能需要额外的屏幕录制工具支持

## 故障排除

1. **元素定位失败**: 检查路由器界面是否有变化，可能需要更新元素定位策略
2. **登录失败**: 检查用户名和密码是否正确
3. **浏览器驱动问题**: 确保网络连接正常，可以访问ChromeDriver下载地址
4. **权限问题**: 确保脚本有足够的权限运行
5. **录制问题**: 确保已安装并正确配置了屏幕录制工具

