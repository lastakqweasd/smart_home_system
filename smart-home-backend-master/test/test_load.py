import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
from locust import events
import json

# 配置测试参数
HOST = "http://localhost:8000/api"
LOCUST_FILE = "test_locust.py"  # 上面的测试文件
DURATION = "1m"  # 每次测试持续时间
USERS = list(range(10, 300, 10))  # 从10到300，步长10
SPAWN_RATE = 10  # 每秒启动的用户数
RESULTS_DIR = "test_results"
CSV_PREFIX = "locust_stats"

# 创建结果目录
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# 运行Locust测试并收集结果
def run_load_test(num_users):
    csv_path = f"{RESULTS_DIR}/{CSV_PREFIX}_{num_users}"
    command = [
        "locust",
        "-f", LOCUST_FILE,
        "--host", HOST,
        "--headless",
        "--users", str(num_users),
        "--spawn-rate", str(SPAWN_RATE),
        "--run-time", DURATION,
        "--csv", csv_path,
        "--only-summary"
    ]
    
    print(f"正在测试 {num_users} 用户...")
    start_time = time.time()
    subprocess.run(command)
    elapsed = time.time() - start_time
    print(f"完成 {num_users} 用户测试，耗时 {elapsed:.2f} 秒")
    
    # 读取结果
    stats = pd.read_csv(f"{csv_path}_stats.csv")
    return stats.iloc[-1]  # 返回汇总行

# 收集所有测试结果
results = []
for user_count in USERS:
    result = run_load_test(user_count)
    result['User Count'] = user_count
    results.append(result)
    time.sleep(5)  # 间隔5秒让系统恢复

# 转换为DataFrame
df = pd.DataFrame(results)

# 保存原始数据
df.to_csv(f"{RESULTS_DIR}/combined_results.csv", index=False)

# 绘制图表
plt.figure(figsize=(15, 10))

# 吞吐量 (RPS)
plt.subplot(2, 2, 1)
plt.plot(df['User Count'], df['Total Requests']/int(DURATION[:-1]), 'b-o')
plt.title('吞吐量 (Requests per Second)')
plt.xlabel('用户数量')
plt.ylabel('RPS')
plt.grid(True)

# 平均响应时间
plt.subplot(2, 2, 2)
plt.plot(df['User Count'], df['Average Response Time'], 'r-o')
plt.title('平均响应时间')
plt.xlabel('用户数量')
plt.ylabel('毫秒')
plt.grid(True)

# 失败率
plt.subplot(2, 2, 3)
plt.plot(df['User Count'], df['Failures']/df['Total Requests']*100, 'g-o')
plt.title('失败率')
plt.xlabel('用户数量')
plt.ylabel('百分比 (%)')
plt.grid(True)

# 90%百分位响应时间
plt.subplot(2, 2, 4)
plt.plot(df['User Count'], df['90%'], 'm-o')
plt.title('90%百分位响应时间')
plt.xlabel('用户数量')
plt.ylabel('毫秒')
plt.grid(True)

plt.tight_layout()
plt.savefig(f"{RESULTS_DIR}/performance_metrics.png")
plt.show()

print("测试完成，结果已保存到", RESULTS_DIR)