import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import pi

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
file_path = "data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 读取季后赛数据以获取gameId映射
postseason_path = "data/Game_postseason_2021-2025.csv"
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")

# 只保留季后赛赛的比赛
df_postseason_games = df_postseason[['gameId']].copy()
df_playoff = df[df['gameId'].isin(df_postseason_games['gameId'])].copy()

# 按年份和gameLabel筛选总决赛数据
df_postseason['year'] = pd.to_datetime(df_postseason['gameDateTimeEst']).dt.year
champions_by_year = {}
champion_team_names = {}  # 存储冠军队伍名称

# 找到每年的NBA东部决赛冠军
for year in [2021, 2022, 2023, 2024, 2025]:
    nba_finals_data = df_postseason[
        (df_postseason['year'] == year) &
        (df_postseason['gameLabel'].isin(['East Conf. Finals', 'East - Conf. Finals']))
    ]

    if not nba_finals_data.empty:
        final_game = nba_finals_data.loc[nba_finals_data['seriesGameNumber'].idxmax()]
        champion_team_id = final_game['winner']
        champions_by_year[year] = champion_team_id

        winner_team_info = df_postseason[
            (df_postseason['gameId'] == final_game['gameId']) &
            (df_postseason['winner'] == champion_team_id)
        ].iloc[0]

        if champion_team_id == winner_team_info['hometeamId']:
            team_name = winner_team_info['hometeamName']
        else:
            team_name = winner_team_info['awayteamName']

        champion_team_names[year] = team_name
        print(f"{year}年NBA总冠军: {team_name} (ID: {champion_team_id})")

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

# 定义要显示的攻防指标（使用标准化后的百分比数据）
metrics = ['off_rat', 'def_rat', 'eFG', 'TS', 'OREB_Per', 'DREB_Per', 'STL_Rat', 'BLK_Rat']
league_averages = [league_avg_off_rat, league_avg_def_rat, league_avg_eFG, league_avg_TSpct,
                   league_avg_OREB_Per, league_avg_DREB_Per, league_avg_STL_Rat, league_avg_BLK_Rat]
metric_names = ['进攻评分', '防守评分', '有效命中率', '真实命中率', '进攻篮板率', '防守篮板率', '抢断率', '盖帽率']

# 计算各年份冠军球队的平均指标（标准化为百分比）
champion_averages = {}
for year, team_id in champions_by_year.items():
    # 获取该年份总决赛的数据
    year_finals_games = df_postseason[
        (df_postseason['year'] == year) &
        (df_postseason['gameLabel'] == 'NBA Finals')
    ]['gameId']

    if len(year_finals_games) > 0:
        year_data = df_playoff[
            (df_playoff['teamId'] == team_id) &
            (df_playoff['gameId'].isin(year_finals_games))
        ]

        if not year_data.empty:
            avg_values = []
            for i, metric in enumerate(metrics):
                team_avg = year_data[metric].mean()
                league_avg = league_averages[i]
                if league_avg != 0:
                    percentage_value = (team_avg / league_avg) * 100
                else:
                    percentage_value = 0
                avg_values.append(percentage_value)
            champion_averages[year] = avg_values

# 创建雷达图
angles=[n/float(len(metric_names))*2*pi for n in range(len(metric_names))]
angles+=angles[:1]

fig,ax=plt.subplots(figsize=(12,12),subplot_kw=dict(projection='polar'))

# 设置环形效果，避免中心区域过于拥挤
ax.set_ylim(50,150)

colors=['red','blue','green','orange','purple','brown','pink','gray']
linestyles = ['-', '--', '-.', ':', '']  # 实线、虚线、点划线、点线、无样式

for idx,(year,values) in enumerate(champion_averages.items()):
    values_copy=values.copy()
    values_copy+=values_copy[:1]

    team_name=champion_team_names.get(year)
    label=f'{year}年{team_name}'

    # 使用不同线型、标记和较低透明度
    ax.plot(angles,values_copy,color=colors[idx%len(colors)],linewidth=2,
            linestyle=linestyles[idx%len(linestyles)],marker='o',markersize=4,label=label)
    ax.fill(angles,values_copy,color=colors[idx%len(colors)],alpha=0.15)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(metric_names)
ax.set_title('21-25赛季历届NBA东部决赛冠军球队攻防指标雷达图',size=16,fontweight='bold',pad=20)
ax.grid(True)
ax.legend(loc='upper right',bbox_to_anchor=(1.1,1.1))

# 添加基准线
baseline=[100]*(len(metric_names)+1)
ax.plot(angles,baseline,color='gray',linewidth=1,linestyle='--',alpha=0.7,label='联盟平均值(100%)')
ax.legend(loc='upper right',bbox_to_anchor=(1.1,1.1))

plt.tight_layout()
plt.show()
