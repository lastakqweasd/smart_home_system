# controllers/device_controller.py
import logging
import os

class DeviceController:
    logger = logging.getLogger("DeviceController")

    log_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../core/device_control.log")
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

        for h in DeviceController.logger.handlers:
            h.flush()
