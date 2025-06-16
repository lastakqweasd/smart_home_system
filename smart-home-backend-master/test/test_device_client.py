import socket
import json
import threading

def simulate_device(host='127.0.0.1', port=9001):
    """模拟设备接收TCP指令的服务端"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"设备模拟器已启动，监听 {host}:{port}...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"\n🔌 收到来自 {addr} 的连接")
            
            # 为每个客户端连接创建新线程
            threading.Thread(
                target=handle_client,
                args=(client_socket,),
                daemon=True
            ).start()

def handle_client(client_socket):
    """处理单个客户端连接"""
    try:
        buffer = b''
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            buffer += chunk
            if b'\n' in buffer:
                break
        
        if buffer:
            # 解析JSON指令
            command_str = buffer.decode('utf-8').strip()
            try:
                command = json.loads(command_str)
                print(f"收到指令: {json.dumps(command, indent=2)}")
                
                # 构造响应
                response = {
                    "status": "success",
                    "message": "指令已执行",
                    "received_command": command,
                    "device_status": "active"
                }
                
                # 发送响应
                client_socket.sendall(
                    (json.dumps(response) + '\n').encode('utf-8')
                )
                print("已发送确认响应")
                
            except json.JSONDecodeError:
                error_msg = "无效的JSON格式"
                client_socket.sendall((error_msg + '\n').encode('utf-8'))
                print(error_msg)
    
    except Exception as e:
        print(f"处理客户端时出错: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    simulate_device()