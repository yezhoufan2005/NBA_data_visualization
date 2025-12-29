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

# 计算分差（球队得分 - 对手得分）
df['score_diff'] = df['PTS'] - df['Opp_PTS']

# 定义分差区间
score_diff_bins = [-float('inf'), -30, -20, -10, 0, 10, 20, 30, float('inf')]
score_diff_labels = ['惨败(-∞,-30)', '大败(-30,-20)', '小败(-20,-10)', '惜败(-10,0)',
                     '险胜(0,10)', '小胜(10,20)', '大胜(20,30)', '狂胜(30,+∞)']

# 将分差分配到区间
df['score_diff_interval'] = pd.cut(df['score_diff'], bins=score_diff_bins,
                                   labels=score_diff_labels, include_lowest=True)

# 获取计算进攻评分和防守评分的所有字段
offense_metrics = [
    'eFG', 'TS', 'AST_Per', 'TOV_Rat', 'OREB_Per'
]
defense_metrics = [
    'Opp_eFG', 'STL_Rat', 'BLK_Rat', 'PF_Rat', 'Opp_TOV_Rat', 'DREB_Per'
]

# 计算每个分差区间的指标平均值
grouped_data = df.groupby('score_diff_interval', observed=False).agg({
    **{metric: 'mean' for metric in offense_metrics},
    **{metric: 'mean' for metric in defense_metrics}
}).round(2)

# 从 team_calculate.py 中获取联盟平均值
league_avg_eFG = df['eFG'].mean()
league_avg_TS = df['TS'].mean()
league_avg_AST_Per = df['AST_Per'].mean()
league_avg_TOV_Rat = df['TOV_Rat'].mean()
league_avg_OREB_Per = df['OREB_Per'].mean()

league_avg_Opp_eFG = df['Opp_eFG'].mean()
league_avg_STL_Rat = df['STL_Rat'].mean()
league_avg_BLK_Rat = df['BLK_Rat'].mean()
league_avg_PF_Rat = df['PF_Rat'].mean()
league_avg_Opp_TOV_Rat = df['Opp_TOV_Rat'].mean()
league_avg_DREB_Per = df['DREB_Per'].mean()

# 创建联盟平均值字典
league_avg_dict = {
    'eFG': league_avg_eFG,
    'TS': league_avg_TS,
    'AST_Per': league_avg_AST_Per,
    'TOV_Rat': league_avg_TOV_Rat,
    'OREB_Per': league_avg_OREB_Per,
    'Opp_eFG': league_avg_Opp_eFG,
    'STL_Rat': league_avg_STL_Rat,
    'BLK_Rat': league_avg_BLK_Rat,
    'PF_Rat': league_avg_PF_Rat,
    'Opp_TOV_Rat': league_avg_Opp_TOV_Rat,
    'DREB_Per': league_avg_DREB_Per
}

# 创建百分比数据表
percent_data = grouped_data.copy()

# 对进攻指标计算百分比
for metric in offense_metrics:
    if metric in league_avg_dict:
        percent_data[metric] = (grouped_data[metric] / league_avg_dict[metric] * 100).round(2)

# 对防守指标计算百分比
for metric in defense_metrics:
    if metric in league_avg_dict:
        if metric in ['Opp_eFG', 'PF_Rat']:  # 逆向值
            percent_data[metric] = (league_avg_dict[metric] / grouped_data[metric] * 100).round(2)
        else:  # 正向值
            percent_data[metric] = (grouped_data[metric] / league_avg_dict[metric] * 100).round(2)

# 创建图表
fig, ax = plt.subplots(figsize=(16, 10))

# 准备数据用于堆叠柱形图
x_pos = np.arange(len(score_diff_labels))
width = 0.7

# 创建颜色映射
colors_offense = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b']
colors_defense = ['#d62728', '#9f3a6e', '#c49c94', '#e5c890', '#c7c7c7', '#2ca02c']

# 绘制进攻端指标
bottom = np.zeros(len(x_pos))
for i, metric in enumerate(offense_metrics):
    values = percent_data[metric].values
    bars = ax.bar(x_pos, values, width, bottom=bottom,
                  label=f'进攻-{metric}', color=colors_offense[i], alpha=0.8)
    # 移除了柱状图上的数值标签
    bottom += values

# 绘制防守端指标
for i, metric in enumerate(defense_metrics):
    values = percent_data[metric].values
    bars = ax.bar(x_pos, values, width, bottom=bottom,
                  label=f'防守-{metric}', color=colors_defense[i], alpha=0.8)
    # 移除了柱状图上的数值标签
    bottom += values

# 为每个指标添加折线，连接每个色块中心
# 计算每个指标在堆叠柱形图中的位置
current_bottom = np.zeros(len(x_pos))
y_positions = []

# 进攻指标
for i, metric in enumerate(offense_metrics):
    values = percent_data[metric].values
    y_center = current_bottom + values / 2
    y_positions.append(y_center)
    current_bottom += values

# 防守指标
for i, metric in enumerate(defense_metrics):
    values = percent_data[metric].values
    y_center = current_bottom + values / 2
    y_positions.append(y_center)
    current_bottom += values

# 绘制折线
for i, pos in enumerate(y_positions):
    if i < len(offense_metrics):
        color = colors_offense[i]  # 进攻指标颜色
        metric_name = offense_metrics[i]  # 获取指标名称
        label_name = f'进攻-{metric_name}'
    else:
        color = colors_defense[i - len(offense_metrics)]  # 防守指标颜色
        metric_name = defense_metrics[i - len(offense_metrics)]  # 获取指标名称
        label_name = f'防守-{metric_name}'

    ax.plot(x_pos, pos, marker='o', linestyle='-', linewidth=2,
            color=color, label=label_name, zorder=5)

    # 为折线上的每个点添加数值标签
    for j, (x, y) in enumerate(zip(x_pos, pos)):
        ax.annotate(f'{y:.1f}%', (x, y),
                   textcoords="offset points", xytext=(0,10), ha='center',
                   fontsize=8, fontweight='bold', color='white')

# 设置图表标题和标签
ax.set_xlabel('分差区间', fontsize=12, fontweight='bold')
ax.set_ylabel('相对于联盟平均值的百分比(%)', fontsize=12, fontweight='bold')
ax.set_title('不同分差区间攻防详细指标堆叠柱形图\n(所有计算进攻评分和防守评分的字段 - 相对联盟平均值)',
             fontsize=14, fontweight='bold', pad=20)

# 设置x轴标签
ax.set_xticks(x_pos)
ax.set_xticklabels(score_diff_labels, rotation=45, ha='right')

# 添加图例
ax.legend(loc='upper left', bbox_to_anchor=(0.01, 0.99), ncol=5, fontsize=10)

# 添加网格线
ax.grid(axis='y', alpha=0.3)

# 调整布局
plt.tight_layout()
plt.show()
