import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from chardet import detect

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# 配置参数
RESULTS_DIR = "test_results"
CSV_PREFIX = "locust_stats"
USER_COUNTS = list(range(10, 310, 10))  # 从10到300，步长10

def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']

def load_locust_data():
    """加载所有Locust测试结果数据"""
    results = []
    
    for user_count in USER_COUNTS:
        stats_file = f"{RESULTS_DIR}/{CSV_PREFIX}_{user_count}_stats.csv"
        
        try:
            # 检测文件编码
            encoding = detect_encoding(stats_file)
            print(f"检测到文件 {stats_file} 的编码: {encoding}")
            
            # 读取统计数据
            stats = pd.read_csv(stats_file, encoding=encoding)
            last_row = stats.iloc[-1].to_dict()  # 获取汇总行
            
            # 读取失败数据
            failures_file = f"{RESULTS_DIR}/{CSV_PREFIX}_{user_count}_failures.csv"
            if os.path.exists(failures_file):
                failures_encoding = detect_encoding(failures_file)
                failures = pd.read_csv(failures_file, encoding=failures_encoding)
                last_row['Total Failures'] = len(failures)
            else:
                last_row['Total Failures'] = 0
            
            last_row['User Count'] = user_count
            results.append(last_row)
            
        except Exception as e:
            print(f"加载文件 {stats_file} 出错: {str(e)}")
            continue
    
    if not results:
        raise ValueError("没有加载到任何测试结果数据")
    
    return pd.DataFrame(results)

def plot_performance_metrics(df):
    """绘制性能指标图表"""
    plt.figure(figsize=(15, 10))
    
    # 确定实际列名（兼容不同Locust版本）
    request_column = 'Total Requests' if 'Total Requests' in df.columns else 'Request Count'
    avg_response_column = 'Average Response Time' if 'Average Response Time' in df.columns else 'Median Response Time'
    percentile_column = '90%' if '90%' in df.columns else '90%ile'
    
    # 1. 吞吐量 (RPS)
    plt.subplot(2, 2, 1)
    if request_column in df.columns:
        # 假设每次测试持续时间为1分钟（60秒）
        rps = df[request_column] / 60  
        plt.plot(df['User Count'], rps, 'b-o')
        plt.title('吞吐量 (Requests per Second)')
        plt.xlabel('用户数量')
        plt.ylabel('请求数/秒 (RPS)')
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, '无吞吐量数据', ha='center', va='center')
        plt.title('吞吐量 (无数据)')
    
    # 2. 平均响应时间
    plt.subplot(2, 2, 2)
    if avg_response_column in df.columns:
        plt.plot(df['User Count'], df[avg_response_column], 'r-o')
        plt.title('平均响应时间')
        plt.xlabel('用户数量')
        plt.ylabel('毫秒')
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, '无响应时间数据', ha='center', va='center')
        plt.title('平均响应时间 (无数据)')
    
    # 3. 失败率
    plt.subplot(2, 2, 3)
    if 'Total Failures' in df.columns and request_column in df.columns:
        failure_rate = (df['Total Failures'] / df[request_column]) * 100
        plt.plot(df['User Count'], failure_rate, 'g-o')
        plt.title('请求失败率')
        plt.xlabel('用户数量')
        plt.ylabel('百分比 (%)')
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, '无失败率数据', ha='center', va='center')
        plt.title('请求失败率 (无数据)')
    
    # 4. 90%百分位响应时间
    plt.subplot(2, 2, 4)
    if percentile_column in df.columns:
        plt.plot(df['User Count'], df[percentile_column], 'm-o')
        plt.title('90%百分位响应时间')
        plt.xlabel('用户数量')
        plt.ylabel('毫秒')
        plt.grid(True)
    else:
        plt.text(0.5, 0.5, '无百分位数据', ha='center', va='center')
        plt.title('90%百分位响应时间 (无数据)')
    
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/performance_metrics.png", dpi=300, bbox_inches='tight')
    plt.show()

def main():
    try:
        # 确保安装了chardet库
        try:
            from chardet import detect
        except ImportError:
            print("正在安装chardet库...")
            import subprocess
            subprocess.run(["pip", "install", "chardet"], check=True)
            from chardet import detect
        
        # 加载数据
        df = load_locust_data()
        print("\n成功加载测试数据:")
        print(df.head())
        
        # 保存合并后的数据
        df.to_csv(f"{RESULTS_DIR}/combined_results.csv", index=False, encoding='utf_8_sig')
        print(f"\n合并后的数据已保存到 {RESULTS_DIR}/combined_results.csv")
        
        # 绘制图表
        plot_performance_metrics(df)
        print(f"\n性能图表已保存到 {RESULTS_DIR}/performance_metrics.png")
        
    except Exception as e:
        print(f"\n程序出错: {str(e)}")

if __name__ == "__main__":
    main()