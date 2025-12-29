import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
file_path ="../data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 读取季后赛数据以获取gameId映射
postseason_path ="../data/Game_postseason_2021-2025.csv"
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")

# 从team_preprocess.py获取数据，添加日期信息
team_preprocess_path ="../data/TeamStatistics_2021-2025.csv"
df_with_date = pd.read_csv(team_preprocess_path, encoding="utf-8")

# 将gameId映射到日期
df_with_date = df_with_date[['gameId', 'gameDateTimeEst']].drop_duplicates()
df = df.merge(df_with_date, on='gameId', how='left', suffixes=('', '_date'))

# 转换日期格式
df['gameDateTimeEst'] = pd.to_datetime(df['gameDateTimeEst'])

# 按年份筛选数据
df['year'] = df['gameDateTimeEst'].dt.year

# 创建球队ID到球队名称的映射
team_id_to_name = {}

# 从postseason数据中获取球队名称映射
for _, row in df_postseason.iterrows():
    team_id_to_name[row['hometeamId']] = row['hometeamName']
    team_id_to_name[row['awayteamId']] = row['awayteamName']

# 按年份和gameLabel筛选总决赛数据
df_postseason['year'] = pd.to_datetime(df_postseason['gameDateTimeEst']).dt.year
champions_by_year = {}
champion_team_names = {}  # 存储冠军队伍名称

# 找到每年的NBA总决赛冠军
available_years = [2021, 2022, 2023, 2024]  # 修正：只包含已有季后赛数据的年份
for year in available_years:
    nba_finals_data = df_postseason[
        (df_postseason['year'] == year) &
        (df_postseason['gameLabel'] == 'NBA Finals')
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

# 计算历史冠军的平均攻防效率
champion_efficiencies = {}
for year, team_id in champions_by_year.items():
    # 获取该年份总决赛的数据
    year_finals_games = df_postseason[
        (df_postseason['year'] == year) &
        (df_postseason['gameLabel'] == 'NBA Finals')
    ]['gameId']

    # 获取该冠军队在总决赛中的数据
    champion_data = df[
        (df['teamId'] == team_id) &
        (df['gameId'].isin(year_finals_games))
    ]

    if not champion_data.empty:
        avg_off_eff = champion_data['off_eff'].mean()
        avg_def_eff = champion_data['def_eff'].mean()
        avg_net_eff = champion_data['net_eff'].mean()

        champion_efficiencies[year] = {
            'off_eff': avg_off_eff,
            'def_eff': avg_def_eff,
            'net_eff': avg_net_eff,
            'team_name': champion_team_names[year]
        }

# 计算当前25-26赛季各队伍的平均攻防效率（常规赛+季后赛）
current_year = 2025  # 当前赛季年份
current_season_data = df[df['year'] == current_year]

# 获取当前赛季的球队ID
current_team_ids = set(current_season_data['teamId'].unique())

# 计算当前赛季各队的平均指标
current_team_averages = {}
for team_id in current_team_ids:
    # 获取该球队的所有当前赛季数据
    team_data = current_season_data[current_season_data['teamId'] == team_id]

    if not team_data.empty and team_id in team_id_to_name:
        avg_off_eff = team_data['off_eff'].mean()
        avg_def_eff = team_data['def_eff'].mean()
        avg_net_eff = team_data['net_eff'].mean()

        team_name = team_id_to_name[team_id]
        current_team_averages[team_name] = {
            'off_eff': avg_off_eff,
            'def_eff': avg_def_eff,
            'net_eff': avg_net_eff
        }

# 计算各球队的综合评分
team_scores = {}
for team_name, stats in current_team_averages.items():
    score = (stats['off_eff'] - stats['def_eff']) + stats['net_eff']
    team_scores[team_name] = score

# 创建散点图
fig, ax = plt.subplots(figsize=(14, 10))

# 绘制当前赛季球队 - 气泡大小反映净效率，颜色反映综合评分
current_teams_x = [team['off_eff'] for team in current_team_averages.values()]
current_teams_y = [team['def_eff'] for team in current_team_averages.values()]
current_teams_names = list(current_team_averages.keys())
current_teams_net_eff = [team['net_eff'] for team in current_team_averages.values()]
current_teams_scores = [team_scores[team_name] for team_name in current_teams_names]

# 归一化气泡大小（净效率）
min_net_eff = min(current_teams_net_eff)
max_net_eff = max(current_teams_net_eff)
# 将净效率映射到气泡大小
bubble_sizes = [(net_eff - min_net_eff) / (max_net_eff - min_net_eff) * 270 + 30 for net_eff in current_teams_net_eff]

# 归一化颜色（综合评分）
min_score = min(current_teams_scores)
max_score = max(current_teams_scores)
# 使用颜色映射
colors = [(score - min_score) / (max_score - min_score) if max_score != min_score else 0.5 for score in current_teams_scores]

scatter1 = ax.scatter(current_teams_x, current_teams_y,
                     s=bubble_sizes, alpha=0.6, c=colors,
                     cmap='viridis', edgecolors='black', linewidth=0.8,
                     label='当前赛季球队', zorder=3)

# 标注当前赛季球队
for i, team_name in enumerate(current_teams_names):
    ax.annotate(team_name, (current_teams_x[i], current_teams_y[i]),
               xytext=(5, 5), textcoords='offset points',
               fontsize=9, ha='left', va='bottom',
               alpha=0.7)

# 绘制历史冠军球队 - 使用固定大小的红色星标，不使用综合评分
champion_x = [champ['off_eff'] for champ in champion_efficiencies.values()]
champion_y = [champ['def_eff'] for champ in champion_efficiencies.values()]
champion_names = [f"{champ['team_name']} ({year})"
                  for year, champ in champion_efficiencies.items()]

scatter2 = ax.scatter(champion_x, champion_y,
                     s=200, alpha=0.8, c='red',
                     edgecolors='darkred', linewidth=1.5,
                     marker='*', label='历史总冠军', zorder=4)

# 标注历史冠军球队
for i, champ_name in enumerate(champion_names):
    ax.annotate(champ_name, (champion_x[i], champion_y[i]),
               xytext=(10, 10), textcoords='offset points',
               fontsize=10, ha='left', va='bottom',
               weight='bold', color='darkred')

# 添加图例
ax.legend(loc='upper left', fontsize=12)

# 设置坐标轴标签
ax.set_xlabel('进攻效率 (Offensive Efficiency)', fontsize=12, fontweight='bold')
ax.set_ylabel('防守效率 (Defensive Efficiency)', fontsize=12, fontweight='bold')

# 添加网格
ax.grid(True, alpha=0.3, zorder=1)

# 设置标题
ax.set_title('当前赛季球队与历史总冠军攻防效率对比散点图\n(气泡大小表示净效率，颜色表示综合评分，星标为历史总冠军)',
             fontsize=14, fontweight='bold', pad=20)

ax.invert_yaxis()

# 添加等效率线
league_avg_off_eff = df['off_eff'].mean()
league_avg_def_eff = df['def_eff'].mean()

# 添加联盟平均线
ax.axhline(y=league_avg_def_eff, color='gray', linestyle='--', alpha=0.5, label='联盟平均防守效率')
ax.axvline(x=league_avg_off_eff, color='gray', linestyle='--', alpha=0.5, label='联盟平均进攻效率')

# 添加颜色编码的综合评分图例
sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=min_score, vmax=max_score))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label('综合评分', rotation=270, labelpad=15)

# 调整布局
plt.tight_layout()
plt.show()

# 预测潜在冠军队伍
print("\n根据攻防效率预测潜在冠军队伍:")
potential_champions = []
for team, stats in current_team_averages.items():
    score = (stats['off_eff'] - stats['def_eff']) + stats['net_eff']
    potential_champions.append((team, score))

potential_champions.sort(key=lambda x: x[1], reverse=True)
print("基于攻防效率的冠军预测:")
for i, (team, score) in enumerate(potential_champions[:5]):
    print(f"{i+1}. {team}: 综合评分 {score:.2f}")
