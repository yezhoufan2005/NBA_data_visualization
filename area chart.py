import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 读取数据
file_path = "data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 读取常规赛和季后赛数据以获取gameId映射
regular_season_path = "data/Game_regularseason_2021-2025.csv"
postseason_path = "data/Game_postseason_2021-2025.csv"

df_regular = pd.read_csv(regular_season_path, encoding="utf-8")
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")

# 合并常规赛和季后赛的游戏ID
all_valid_games = pd.concat([df_regular[['gameId']], df_postseason[['gameId']]], ignore_index=True)
all_valid_game_ids = set(all_valid_games['gameId'].tolist())

# 只保留常规赛或季后赛的比赛
df = df[df['gameId'].isin(all_valid_game_ids)]

# 从team_preprocess.py获取数据，添加日期信息
team_preprocess_path = "data/TeamStatistics_2021-2025.csv"
df_with_date = pd.read_csv(team_preprocess_path, encoding="utf-8")

# 将gameId映射到日期 - 使用suffixes参数避免列名冲突
df_with_date = df_with_date[['gameId', 'gameDateTimeEst']].drop_duplicates()
df = df.merge(df_with_date, on='gameId', how='left', suffixes=('', '_date'))

# 转换日期格式
df['gameDateTimeEst'] = pd.to_datetime(df['gameDateTimeEst'])

# 按实际比赛时间分组（非按日历日期）
daily_stats = df.groupby('gameDateTimeEst').agg({
    'off_rat': 'mean',
    'def_rat': 'mean',
    'net_rat': 'mean'
}).round(2).reset_index()

# 计算评分变化（差分）
daily_stats['off_rat_diff'] = daily_stats['off_rat'].diff()
daily_stats['def_rat_diff'] = daily_stats['def_rat'].diff()
daily_stats['net_rat_diff'] = daily_stats['off_rat'].diff()-daily_stats['def_rat'].diff()

# 清除无数据的行（包括原始值和差分值）
daily_stats = daily_stats.dropna(subset=['off_rat', 'def_rat', 'net_rat', 'off_rat_diff', 'def_rat_diff', 'net_rat_diff'])

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建图形
fig, ax = plt.subplots(figsize=(16, 10))

# 绘制进攻评分变化
ax.plot(daily_stats['gameDateTimeEst'], daily_stats['off_rat_diff'],
        color='blue', linewidth=1.5, label='进攻评分变化', alpha=0.8)

# 绘制防守评分变化
ax.plot(daily_stats['gameDateTimeEst'], daily_stats['def_rat_diff'],
        color='red', linewidth=1.5, label='防守评分变化', alpha=0.8)

# 添加净评分变化线
ax2 = ax.twinx()
ax2.plot(daily_stats['gameDateTimeEst'], daily_stats['net_rat_diff'],
         color='purple', linewidth=2, label='净评分变化', marker='o', markersize=3)
ax2.set_ylabel('净评分变化', color='purple', fontsize=12)

ax.set_title('2021-2025年度攻防评分变化趋势（常规赛+季后赛）', fontsize=16, fontweight='bold')
ax.set_xlabel('时间', fontsize=12)
ax.set_ylabel('评分变化', fontsize=12)
ax.grid(True, alpha=0.3)

# 合并图例
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

plt.tight_layout()
plt.show()
