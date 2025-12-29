import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
file_path ="../data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 获取各队的平均总评分
team_net_rat = df.groupby('teamId')['net_rat'].mean().sort_values(ascending=False)

# 获取评分最高的10支队伍
top_teams = team_net_rat.head(10)

# 创建球队ID到球队名称的映射
team_id_to_name = {}
postseason_path ="../data/Game_postseason_2021-2025.csv"
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")
for _, row in df_postseason.iterrows():
    team_id_to_name[row['hometeamId']] = row['hometeamName']
    team_id_to_name[row['awayteamId']] = row['awayteamName']

# 计算联盟平均值（用于标准化）
league_avg_off_rat = df['off_rat'].mean()
league_avg_def_rat = df['def_rat'].mean()
league_avg_eFG = df['eFG'].mean()
league_avg_TS = df['TS'].mean()
league_avg_OREB_Per = df['OREB_Per'].mean()
league_avg_DREB_Per = df['DREB_Per'].mean()
league_avg_STL_Rat = df['STL_Rat'].mean()
league_avg_BLK_Rat = df['BLK_Rat'].mean()

# 定义要显示的攻防指标
metrics = ['off_rat', 'def_rat', 'eFG', 'TS', 'OREB_Per', 'DREB_Per', 'STL_Rat', 'BLK_Rat']
league_averages = [league_avg_off_rat, league_avg_def_rat, league_avg_eFG, league_avg_TS,
                   league_avg_OREB_Per, league_avg_DREB_Per, league_avg_STL_Rat, league_avg_BLK_Rat]
metric_names = ['进攻评分', '防守评分', '有效命中率', '真实命中率', '进攻篮板率', '防守篮板率', '抢断率', '盖帽率']

# 获取高评分队伍的核心攻防指标平均值（标准化为百分比）
high_scoring_teams_data = {}
for team_id in top_teams.index:
    team_data = df[df['teamId'] == team_id]
    if not team_data.empty and team_id in team_id_to_name:
        team_averages = []
        for i, metric in enumerate(metrics):
            team_avg = team_data[metric].mean()
            league_avg = league_averages[i]
            if league_avg != 0:
                percentage_value = (team_avg / league_avg) * 100
            else:
                percentage_value = 0
            team_averages.append(percentage_value)

        team_name = team_id_to_name[team_id]
        high_scoring_teams_data[team_name] = dict(zip(metrics, team_averages))

# 选择评分最高的10支队伍进行哑铃图展示
top_5_teams = dict(list(high_scoring_teams_data.items())[:10])

# 创建哑铃图
fig, ax = plt.subplots(figsize=(14, 10))

# 使用深色自定义调色板
colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

# 为每个指标设置标签和颜色
for idx, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
    for i, (team_name, team_data) in enumerate(top_5_teams.items()):
        value = team_data[metric]
        ax.plot([100, value], [i + idx*0.1, i + idx*0.1], color=colors[idx], linewidth=2.5, alpha=1.0)
        ax.scatter([100, value], [i + idx*0.1, i + idx*0.1], color=colors[idx], s=120, alpha=1.0, zorder=3)

        # 添加数值标签
        ax.annotate(f'{value:.1f}%', (value, i + idx*0.1),
                   textcoords="offset points", xytext=(10,0), ha='left',
                   fontsize=9, alpha=0.8)

# 设置坐标轴
ax.set_yticks(np.arange(len(top_5_teams)))
ax.set_yticklabels(list(top_5_teams.keys()), fontsize=10)
ax.set_xlabel('相对于联盟平均值的百分比 (%)', fontsize=12)
ax.set_ylabel('球队', fontsize=12)
ax.set_title('高总评分Top10队伍核心攻防指标对比哑铃图', fontsize=14, fontweight='bold')

# 添加网格
ax.grid(True, alpha=0.3)

# 添加100%基准线（联盟平均值）
ax.axvline(x=100, color='gray', linestyle='--', alpha=0.5, label='联盟平均值(100%)')

# 为每个队伍添加虚线分隔线
for i in range(len(top_5_teams)):
    ax.axhline(y=i, color='black', linestyle='--', alpha=0.3, linewidth=0.8)

# 图例
handles = [plt.Line2D([0], [0], color=colors[i], lw=2, label=metric_names[i]) for i in range(len(metrics))]
ax.legend(handles=handles, loc='upper right')

plt.tight_layout()
plt.show()
