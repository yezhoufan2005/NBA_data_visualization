import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 读取数据
file_path ="../data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 读取常规赛数据以获取gameId映射
regular_season_path ="../data/Game_regularseason_2021-2025.csv"
df_regular = pd.read_csv(regular_season_path, encoding="utf-8")

# 只保留常规赛的比赛
df_regular_games = df_regular[['gameId']].copy()
df = df[df['gameId'].isin(df_regular_games['gameId'])]

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 核心指标
metrics = ['PTS', 'Opp_PTS', 'eFG', 'Opp_eFG', 'off_rat', 'def_rat']
metric_names = ['得分', '对手得分', '有效命中率', '对手有效命中率', '进攻评分', '防守评分']

# 创建分组箱线图
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('常规赛赢球队伍核心攻防指标箱线图', fontsize=16, fontweight='bold')

# 顺序排列指标
metrics_order = [
    ('PTS', '得分'),
    ('eFG', '有效命中率'),
    ('off_rat', '进攻评分'),
    ('Opp_PTS', '对手得分'),
    ('Opp_eFG', '对手有效命中率'),
    ('def_rat', '防守评分')
]

for i, (metric, name) in enumerate(metrics_order):
    row = i // 3
    col = i % 3

    # 按胜负分组
    win_data = df[df['win'] == 1][metric]
    lose_data = df[df['win'] == 0][metric]

    # 创建分组箱线图
    sns.boxplot(data=[win_data, lose_data], ax=axes[row, col])
    axes[row, col].set_xticklabels(['赢球', '输球'])
    axes[row, col].set_title(f'{name}对比')
    axes[row, col].set_ylabel(name)

    # 添加网格线
    axes[row, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
