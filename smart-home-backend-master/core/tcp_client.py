import socket
import json

def send_tcp_command(host='172.20.10.3', port=9000, command=None, timeout=5):
    if command is None:
        command = {
            "operation": "control",   # 必须加上
            "device_id": 1,
            "action": "toggle"
        }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))

            message = json.dumps(command) + '\n'
            s.sendall(message.encode('utf-8'))

            buffer = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                if b'\n' in buffer:
                    break

            response = buffer.decode('utf-8').strip()
            print("服务器回复:", response)

    except socket.timeout:
        print(f"连接或接收超时 (>{timeout}s)")
    except Exception as e:
        print("连接或发送失败:", e)


