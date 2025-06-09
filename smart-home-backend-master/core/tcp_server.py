import socketserver
import json
import socket
import logging
from contextlib import closing
from threading import Thread
from .models import Device, Room
from .controller import DeviceController

# 单例日志配置
_logger_configured = False

def configure_logger():
    global _logger_configured
    if _logger_configured:
        return

    logger = logging.getLogger("DeviceTCP")
    logger.setLevel(logging.INFO)

    # 清除已有处理器（避免重复）
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 文件日志配置
    file_handler = logging.FileHandler('./logs/tcp.log', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _logger_configured = True


class TCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        configure_logger()
        logger = logging.getLogger("DeviceTCP")

        try:
            raw_data = self.request.recv(1024).decode('utf-8')
            logger.info(f"收到TCP请求: {raw_data}")

            command = json.loads(raw_data)
            response = self.handle_tcp_command(command)
            self.request.sendall((json.dumps(response) + "\n").encode('utf-8'))
            logger.info(f"已响应TCP请求: {response}")

        except json.JSONDecodeError:
            error = {"error": "无效的JSON格式"}
            self.request.sendall(json.dumps(error).encode('utf-8'))
            logger.error("JSON解析失败")
        except Exception as e:
            error = {"error": str(e)}
            self.request.sendall(json.dumps(error).encode('utf-8'))
            logger.exception("TCP处理异常")

    @staticmethod
    def control(device):
        DeviceController.control(device)

    @classmethod
    def handle_tcp_command(cls, command):
        operation = command.get('operation')
        logger = logging.getLogger("DeviceTCP")

        try:
            if operation == 'query':
                device_id = command.get('id')
                device = Device.objects.get(pk=device_id)
                return {
                    'status': 'success',
                    'device': {
                        'id': device.id,
                        'name': device.name,
                        'type': device.type,
                        'room': device.room.id if device.room else None,
                        'status': device.status,
                        'extra': device.extra,
                        'brand': device.brand,
                    }
                }

            elif operation == 'create':
                room_id = command.get('room')
                if room_id is None:
                    return {'error': '缺少room'}
                room = Room.objects.get(pk=room_id)

                device = Device.objects.create(
                    name=command.get('name'),
                    type=command.get('type'),
                    room=room,
                    status=command.get('status', False),
                    extra=command.get('extra', {}),
                    brand=command.get('brand')
                )
                cls.control(device)
                return {'status': 'success', 'device_id': device.id}

            elif operation == 'update':
                device_id = command.get('id')
                device = Device.objects.get(pk=device_id)

                # 更新字段
                if 'room' in command:
                    room = Room.objects.get(pk=command['room'])
                    device.room = room
                if 'name' in command:
                    device.name = command['name']
                if 'type' in command:
                    device.type = command['type']
                if 'status' in command:
                    device.status = command['status']
                if 'extra' in command:
                    device.extra = command['extra']
                if 'brand' in command:
                    device.brand = command['brand']

                device.save()
                cls.control(device)
                return {'status': 'success', 'device_id': device.id}

            elif operation == 'delete':
                device_id = command.get('id')
                device = Device.objects.get(pk=device_id)
                device.delete()
                return {'status': 'success', 'message': f'设备 {device_id} 已删除'}

            elif operation == 'control':
                device_id = command.get('id')
                device = Device.objects.get(pk=device_id)
                action = command.get('action')

                if action == 'toggle':
                    device.status = not device.status
                elif action == 'set':
                    device.extra.update(command.get('params', {}))

                device.save()
                cls.control(device)
                return {
                    'status': 'success',
                    'device_id': device.id,
                    'current_status': device.status,
                    'extra': device.extra
                }

            else:
                return {'error': '未知操作'}

        except Device.DoesNotExist:
            logger.error("设备不存在")
            return {'error': '设备不存在'}
        except Room.DoesNotExist:
            logger.error("房间不存在")
            return {'error': '房间不存在'}
        except Exception as e:
            logger.exception(f"操作失败: {str(e)}")
            return {'error': f'操作失败: {str(e)}'}


def check_port_available(port):
    """检查端口是否可用"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(1)
        return s.connect_ex(('localhost', port)) != 0

def start_tcp_server(host='0.0.0.0', port=9000):
    configure_logger()
    logger = logging.getLogger("DeviceTCP")

    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        test_socket.bind((host, port))
        test_socket.close()

        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer((host, port), TCPRequestHandler)

        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        print(f"TCP服务正在监听：{host}:{port}")
        logger.info(f"TCP服务正在监听：{host}:{port}")
        return True

    except OSError as e:
        logger.warning(f"端口 {port} 被占用: {e}")
        test_socket.close()
        return False
    except Exception as e:
        logger.exception("TCP服务启动异常")
        return False



# 测试用（直接运行此文件时启动）
if __name__ == "__main__":
    print("测试tcp_server")
    start_tcp_server()