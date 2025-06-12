from core.tcp_client import send_tcp_command

if __name__ == "__main__":
    command = {
        "operation": "create",  # 这是关键字段
        "id": 18,
        "name": "台灯",
        "type": "light",
        "room": 1,  # 注意是 room
        "status": True,
        "extra": {
            "brightness": 80,
            "color": "#FFDD88"
        },
        "brand": None
    }
    send_tcp_command(command=command)
