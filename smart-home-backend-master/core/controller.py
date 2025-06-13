# controllers/device_controller.py
import logging
import os
from .models import Device
from .tcp_client import send_tcp_command

class DeviceController:
    logger = logging.getLogger("DeviceController")

    log_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../logs/device_control.log")
    )
    print("日志写入路径：", log_file_path)

    # 清空所有已有 handlers（避免多次添加）
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    @staticmethod
    def control(device):
        command_info = (
            f"[仿真控制设备] 设备: {device.name} (类型: {device.type})\n"
            f"  - 房间: {device.room.name}\n"
            f"  - 状态: {'开' if device.status else '关'}\n"
            f"  - 配置: {device.extra}\n"
            f"--------------------------------------"
        )

        print(command_info)

        DeviceController.logger.info(
            f"控制设备: {device.name} ({device.type}) 状态={'开' if device.status else '关'} 配置={device.extra}"
        )
        
        # 构造要发送的指令
        command = {
            "operation": "control",
            "id": device.id,
            "action": "set",
            "params": device.extra,
            "status": device.status
        }
        if device.ip_address is not None and device.port is not None:
            send_tcp_command(host=device.ip_address, port=device.port, command=command)

        for h in DeviceController.logger.handlers:
            h.flush()

    @classmethod
    def handle_tcp_command(cls, command):
        try:
            device = Device.objects.get(pk=command['device_id'])

            # 执行指令
            if command['action'] == 'toggle':
                device.status = not device.status
            elif command['action'] == 'set':
                #根据参数修改设备状态，测试时会request.post(url, json=data, headers=headers),这部分json格式的data在core/models.py的69行extra = models.JSONField(default=dict)规定，下面一句话调用update方法更新对应参数
                device.extra.update(command.get('params', {})) 

            device.save()
            cls.control(device)  # 调用原有控制方法

            return {
                'status': 'success',
                'device_id': device.id,
                'current_status': device.status,
                'extra': device.extra
            }
        except Device.DoesNotExist:
            return {'error': '设备不存在'}
        except Exception as e:
            return {'error': f'控制失败: {str(e)}'}
