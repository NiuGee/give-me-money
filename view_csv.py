import pandas as pd

# 读取CSV文件
df = pd.read_csv('ssq_data_20250221.csv')

# 显示前5行数据
print("\n数据预览(前5行):")
print(df.head())

# 显示基本统计信息
print("\n数据统计信息:")
print(f"总期数: {len(df)}")
print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
