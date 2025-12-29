import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
file_path = "data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 读取季后赛数据以获取gameId映射
postseason_path = "data/Game_postseason_2021-2025.csv"
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")

# 只保留季后赛比赛
df_postseason_games = df_postseason[['gameId']].copy()
df_playoff = df[df['gameId'].isin(df_postseason_games['gameId'])].copy()

# 计算联盟平均值（用于标准化）
all_playoff_data = df_playoff.copy()
league_avg_off_rat = all_playoff_data['off_rat'].mean()
league_avg_def_rat = all_playoff_data['def_rat'].mean()
league_avg_eFG = all_playoff_data['eFG'].mean()
league_avg_TSpct = all_playoff_data['TS'].mean()
league_avg_OREB_Per = all_playoff_data['OREB_Per'].mean()
league_avg_DREB_Per = all_playoff_data['DREB_Per'].mean()
league_avg_STL_Rat = all_playoff_data['STL_Rat'].mean()
league_avg_BLK_Rat = all_playoff_data['BLK_Rat'].mean()

# 创建球队ID到球队名称的映射
team_id_to_name = {}
for _, row in df_postseason.iterrows():
    team_id_to_name[row['hometeamId']] = row['hometeamName']
    team_id_to_name[row['awayteamId']] = row['awayteamName']

# 获取所有季后赛球队ID
playoff_team_ids = set(df_playoff['teamId'].unique())

# 计算各季后赛球队的平均指标
team_averages = {}
for team_id in playoff_team_ids:
    # 获取该球队的所有季后赛数据
    team_data = df_playoff[df_playoff['teamId'] == team_id]

    if not team_data.empty and team_id in team_id_to_name:
        # 计算各项指标相对于联盟平均的百分比
        avg_values = []
        metrics = ['off_rat', 'def_rat', 'eFG', 'TS', 'OREB_Per', 'DREB_Per', 'STL_Rat', 'BLK_Rat']
        league_averages = [
            league_avg_off_rat, league_avg_def_rat, league_avg_eFG, league_avg_TSpct,
            league_avg_OREB_Per, league_avg_DREB_Per, league_avg_STL_Rat, league_avg_BLK_Rat
        ]

        for i, metric in enumerate(metrics):
            team_avg = team_data[metric].mean()
            league_avg = league_averages[i]
            if league_avg != 0:
                percentage_value = (team_avg / league_avg) * 100
            else:
                percentage_value = 0
            avg_values.append(percentage_value)

        team_name = team_id_to_name[team_id]
        team_averages[team_name] = avg_values

# 创建热力图数据框
metrics_names = ['进攻评分', '防守评分', '有效命中率', '真实命中率', '进攻篮板率', '防守篮板率', '抢断率', '盖帽率']

# 创建DataFrame
heatmap_data = pd.DataFrame.from_dict(team_averages, orient='index', columns=metrics_names)
heatmap_data.index.name = 'Team'

# 创建热力图
plt.figure(figsize=(14, 10))

# 使用seaborn创建热力图
sns.heatmap(
    heatmap_data,
    annot=True,  # 显示数值
    fmt='.1f',   # 保留一位小数
    cmap='RdYlGn',  # 颜色映射：红-黄-绿
    center=100,     # 以100为中心值（联盟平均值）
    cbar_kws={'label': '相对于联盟平均值的百分比 (%)'},
    linewidths=0.5  # 单元格边框
)

plt.title('季后赛球队核心攻防指标热力图\n(数值表示相对于联盟平均值的百分比)',
            fontsize=16, fontweight='bold', pad=20)
plt.xlabel('攻防指标', fontsize=12)
plt.ylabel('球队名称', fontsize=12)

# 旋转y轴标签以便阅读
plt.yticks(rotation=0)
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
