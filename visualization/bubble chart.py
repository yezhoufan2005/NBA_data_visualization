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

# 创建气泡图
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('常规赛攻防指标与胜负关系气泡图', fontsize=16, fontweight='bold')

# 按胜负分组数据
win_data = df[df['win'] == 1]
lose_data = df[df['win'] == 0]

# 1. 进攻评分 vs 防守评分（气泡大小表示总评分）
scatter1 = axes[0, 0].scatter(lose_data['off_rat'], lose_data['def_rat'],
                            s=(lose_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='blue', label='输球', edgecolors='black', linewidth=0.5)
scatter2 = axes[0, 0].scatter(win_data['off_rat'], win_data['def_rat'],
                            s=(win_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='red', label='赢球', edgecolors='black', linewidth=0.5)
axes[0, 0].set_xlabel('进攻评分')
axes[0, 0].set_ylabel('防守评分')
axes[0, 0].set_title('进攻评分 vs 防守评分（气泡大小表示总评分）')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 2. 有效命中率 vs 对手有效命中率（气泡大小表示总评分）
scatter3 = axes[0, 1].scatter(lose_data['eFG'], lose_data['Opp_eFG'],
                            s=(lose_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='blue', label='输球', edgecolors='black', linewidth=0.5)
scatter4 = axes[0, 1].scatter(win_data['eFG'], win_data['Opp_eFG'],
                            s=(win_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='red', label='赢球', edgecolors='black', linewidth=0.5)
axes[0, 1].set_xlabel('有效命中率')
axes[0, 1].set_ylabel('对手有效命中率')
axes[0, 1].set_title('有效命中率 vs 对手有效命中率（气泡大小表示总评分）')
axes[0, 1].invert_yaxis()
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 3. 进攻篮板 vs 防守篮板（气泡大小表示总评分）
scatter5 = axes[1, 0].scatter(lose_data['OREB_Per'], lose_data['DREB_Per'],
                            s=(lose_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='blue', label='输球', edgecolors='black', linewidth=0.5)
scatter6 = axes[1, 0].scatter(win_data['OREB_Per'], win_data['DREB_Per'],
                            s=(win_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='red', label='赢球', edgecolors='black', linewidth=0.5)
axes[1, 0].set_xlabel('进攻篮板')
axes[1, 0].set_ylabel('防守篮板')
axes[1, 0].set_title('进攻篮板 vs 防守篮板（气泡大小表示总评分）')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 4. 失误率 vs 对手失误率（气泡大小表示总评分）
scatter7 = axes[1, 1].scatter(lose_data['TOV_Rat'], lose_data['Opp_TOV_Rat'],
                            s=(lose_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='blue', label='输球', edgecolors='black', linewidth=0.5)
scatter8 = axes[1, 1].scatter(win_data['TOV_Rat'], win_data['Opp_TOV_Rat'],
                            s=(win_data['net_rat'] - df['net_rat'].min() + 1) * 5,
                            alpha=0.6, c='red', label='赢球', edgecolors='black', linewidth=0.5)
axes[1, 1].set_xlabel('失误率')
axes[1, 1].set_ylabel('对手失误率')
axes[1, 1].set_title('失误率 vs 对手失误率（气泡大小表示总评分）')
axes[1, 1].invert_xaxis()
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 创建单独的气泡图展示净效率与胜负的关系
plt.figure(figsize=(12, 8))
plt.scatter(df['off_eff'], df['def_eff'],
           s=(df['net_eff'] - df['net_eff'].min() + 2) * 10,
           c=df['win'], alpha=0.6, cmap='bwr', edgecolors='black', linewidth=0.5)
plt.xlabel('进攻效率', fontsize=12)
plt.ylabel('防守效率', fontsize=12)
plt.title('常规赛攻防效率与胜负关系气泡图\n(气泡颜色表示胜负, 大小表示净效率)', fontsize=14, fontweight='bold')
plt.colorbar(label='胜负 (0=输球, 1=赢球)')
plt.grid(True, alpha=0.3)
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
