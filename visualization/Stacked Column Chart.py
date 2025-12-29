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

# 计算每个分差区间的攻防指标平均值
grouped_data = df.groupby('score_diff_interval').agg({
    'off_rat': 'mean',      # 进攻评分
    'def_rat': 'mean',      # 防守评分
    'off_eff': 'mean',      # 进攻效率
    'def_eff': 'mean',      # 防守效率
    'net_rat': 'mean',      # 总评分
    'net_eff': 'mean'       # 净效率
}).round(2)

# 为堆叠柱形图准备数据
# 使用进攻评分和防守评分作为攻防贡献的指标
offense_data = grouped_data['off_rat']
defense_data = grouped_data['def_rat']

# 计算攻防贡献占比
total_contribution = offense_data + defense_data
offense_contribution_ratio = (offense_data / total_contribution) * 100
defense_contribution_ratio = (defense_data / total_contribution) * 100

# 创建图表
fig, ax = plt.subplots(figsize=(14, 8))

# 计算堆叠柱形图的位置
x_pos = np.arange(len(score_diff_labels))

# 创建堆叠柱形图
bars1 = ax.bar(x_pos, offense_contribution_ratio.values, label='进攻贡献占比',
               color='skyblue', alpha=0.8)
bars2 = ax.bar(x_pos, defense_contribution_ratio.values, bottom=offense_contribution_ratio.values,
               label='防守贡献占比', color='lightcoral', alpha=0.8)

# 添加数值标签
for i, (off_val, def_val) in enumerate(zip(offense_contribution_ratio.values, defense_contribution_ratio.values)):
    # 进攻贡献占比标签
    ax.text(i, off_val/2, f'{off_val:.1f}%', ha='center', va='center',
            fontsize=10, fontweight='bold', color='darkblue')
    # 防守贡献占比标签
    ax.text(i, off_val + def_val/2, f'{def_val:.1f}%', ha='center', va='center',
            fontsize=10, fontweight='bold', color='darkred')

# 设置图表标题和标签
ax.set_xlabel('分差区间', fontsize=12, fontweight='bold')
ax.set_ylabel('贡献占比(%)', fontsize=12, fontweight='bold')
ax.set_title('常规赛不同分差区间攻防贡献占比堆叠柱形图',
             fontsize=14, fontweight='bold', pad=20)

# 设置x轴标签
ax.set_xticks(x_pos)
ax.set_xticklabels(score_diff_labels, rotation=45, ha='right')

# 添加图例
ax.legend(loc='upper left', fontsize=11)

# 添加网格线
ax.grid(axis='y', alpha=0.3)

# 调整布局
plt.tight_layout()
plt.show()
