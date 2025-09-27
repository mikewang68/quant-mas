import socket
import struct
import time

def check_router_connections(router_ip):
    """检查路由器的网络连接"""
    print(f"检查路由器 {router_ip} 的网络连接...")

    try:
        # 创建TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        # 尝试连接路由器的常见端口
        ports_to_check = [80, 443, 23, 22, 161, 162]  # HTTP, HTTPS, Telnet, SSH, SNMP

        for port in ports_to_check:
            try:
                result = sock.connect_ex((router_ip, port))
                if result == 0:
                    print(f"  端口 {port}: 开放")
                else:
                    print(f"  端口 {port}: 关闭")
            except Exception as e:
                print(f"  端口 {port}: 检查失败 - {e}")

        sock.close()

    except Exception as e:
        print(f"检查连接时出错: {e}")

def send_udp_control_packet(router_ip):
    """尝试发送UDP控制包"""
    print(f"尝试向路由器 {router_ip} 发送UDP控制包...")

    try:
        # 创建UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)

        # 构造控制数据包（这只是示例，实际格式需要根据路由器协议确定）
        control_data = b"\x01\x02\x03\x04"  # 示例控制数据

        # 发送数据包
        sock.sendto(control_data, (router_ip, 520))  # 520是RIP端口，用作示例

        # 等待响应
        try:
            response, addr = sock.recvfrom(1024)
            print(f"收到响应: {response} from {addr}")
        except socket.timeout:
            print("没有收到响应")

        sock.close()

    except Exception as e:
        print(f"发送UDP控制包时出错: {e}")

def main():
    ROUTER_IP = "192.168.1.1"

    print("网络连接检查工具")
    print(f"路由器IP: {ROUTER_IP}")

    # 检查连接
    check_router_connections(ROUTER_IP)

    # 尝试发送控制包
    send_udp_control_packet(ROUTER_IP)

if __name__ == "__main__":
    main()

