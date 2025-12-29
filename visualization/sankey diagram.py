import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
file_path ="../data/TeamStatisticsWithOpponent_2021-2025.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# 读取季后赛数据以获取gameId映射
postseason_path ="../data/Game_postseason_2021-2025.csv"
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")

# 只保留季后赛比赛
df_postseason_games = df_postseason[['gameId']].copy()
df_playoff = df[df['gameId'].isin(df_postseason_games['gameId'])].copy()

# 为每个球队计算攻防评分并分类
def classify_team_type(row):
    """
    根据进攻评分和防守评分对球队进行分类
    """
    off_rat = row['off_rat']
    def_rat = row['def_rat']

    # 基于联盟平均值进行分类
    if off_rat > 105 and def_rat < 100:  # 进攻强，防守强
        return '攻防均衡型'
    elif off_rat > 105 and def_rat >= 100:  # 进攻强，防守弱
        return '进攻主导型'
    elif off_rat <= 105 and def_rat < 100:  # 进攻弱，防守强
        return '防守主导型'
    else:
        return '攻防平均型'

# 标准化轮次名称
def standardize_round_name(round_name):
    if pd.isna(round_name):
        return round_name
    round_name = str(round_name).strip()
    # 统一西部决赛
    if 'West' in round_name and ('Conf. Finals' in round_name or 'Conf Finals' in round_name):
        return 'West - Conf. Finals'
    # 统一东部决赛
    elif 'East' in round_name and ('Conf. Finals' in round_name or 'Conf Finals' in round_name):
        return 'East - Conf. Finals'
    # 统一西部半决赛
    elif 'West' in round_name and ('Semifinals' in round_name or 'Semis' in round_name):
        return 'West - Conf. Semifinals'
    # 统一东部半决赛
    elif 'East' in round_name and ('Semifinals' in round_name or 'Semis' in round_name):
        return 'East - Conf. Semifinals'
    # 统一首轮
    elif 'First Round' in round_name:
        return 'West - First Round' if 'West' in round_name else 'East - First Round'
    # NBA总决赛保持不变
    elif 'NBA Finals' in round_name:
        return 'NBA Finals'
    return round_name  # 其他情况原样返回

# 计算联盟平均值作为基准
league_avg_off_rat = df_playoff['off_rat'].mean()
league_avg_def_rat = df_playoff['def_rat'].mean()

# 为数据添加类型列
df_playoff['off_rat_normalized'] = df_playoff['off_rat']
df_playoff['def_rat_normalized'] = df_playoff['def_rat']
df_playoff['team_type'] = df_playoff.apply(classify_team_type, axis=1)

# 获取每年的总冠军球队
df_postseason['year'] = pd.to_datetime(df_postseason['gameDateTimeEst']).dt.year
champions_by_year = {}

# 找到每年的NBA总决赛冠军
for year in [2021, 2022, 2023, 2024, 2025]:
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

        print(f"{year}年NBA总冠军: {team_name} (ID: {champion_team_id})")

# 为每个总冠军球队确定其季后赛路径中的攻防类型
sankey_data = []
for year, team_id in champions_by_year.items():
    # 获取该年季后赛所有比赛
    year_playoff_games = df_postseason[df_postseason['year'] == year]

    # 获取该冠军球队在该年季后赛中的所有比赛数据
    champion_playoff_data = df_playoff[
        (df_playoff['teamId'] == team_id) &
        (df_playoff['gameId'].isin(year_playoff_games['gameId']))
    ].copy()

    if not champion_playoff_data.empty:
        # 获取每轮系列赛信息
        champion_games = df_postseason[
            (df_postseason['year'] == year) &
            ((df_postseason['hometeamId'] == team_id) | (df_postseason['awayteamId'] == team_id))
        ].copy()

        # 按seriesGameNumber排序以确定比赛顺序
        champion_games = champion_games.sort_values(['gameLabel', 'seriesGameNumber'])

        # 获取该球队在每个系列赛的平均攻防类型
        for series_label in champion_games['gameLabel'].unique():
            if pd.notna(series_label):  # 忽略空值
                series_games = champion_games[champion_games['gameLabel'] == series_label]
                series_game_ids = series_games['gameId'].tolist()

                # 获取该系列赛中该球队的数据
                series_data = champion_playoff_data[
                    champion_playoff_data['gameId'].isin(series_game_ids)
                ]

                if not series_data.empty:
                    # 计算该系列赛的平均攻防类型
                    avg_off_rat = series_data['off_rat_normalized'].mean()
                    avg_def_rat = series_data['def_rat_normalized'].mean()

                    # 创建新的行数据
                    standardized_round=standardize_round_name(series_label)
                    row={
                        'year': year,
                        'round': standardized_round,
                        'team_id': team_id,
                        'off_rat': avg_off_rat,
                        'def_rat': avg_def_rat,
                        'team_type': classify_team_type(pd.Series({
                            'off_rat': avg_off_rat,
                            'def_rat': avg_def_rat
                        }))
                    }

                    # 获取球队名称
                    team_info = df_postseason[
                        (df_postseason['gameId'].isin(series_game_ids)) &
                        (df_postseason['winner'] == team_id)
                    ].iloc[0] if not df_postseason[
                        (df_postseason['gameId'].isin(series_game_ids)) &
                        (df_postseason['winner'] == team_id)
                    ].empty else df_postseason[
                        (df_postseason['gameId'].isin(series_game_ids)) &
                        ((df_postseason['hometeamId'] == team_id) | (df_postseason['awayteamId'] == team_id))
                    ].iloc[0]

                    if team_id == team_info['hometeamId']:
                        team_name = team_info['hometeamName']
                    else:
                        team_name = team_info['awayteamName']

                    row['team_name'] = team_name
                    sankey_data.append(row)

# 创建桑基图数据
df_sankey = pd.DataFrame(sankey_data)

# 准备桑基图数据
all_nodes = []
all_nodes.extend(df_sankey['year'].astype(str).tolist())
all_nodes.extend(df_sankey['round'].tolist())
all_nodes.extend(df_sankey['team_type'].tolist())

# 去重并创建节点索引
unique_nodes = list(dict.fromkeys(all_nodes))  # 保持顺序的去重
node_to_index = {node: i for i, node in enumerate(unique_nodes)}

# 创建源节点和目标节点
source = []
target = []
value = []

# 年份 -> 轮次
for _, row in df_sankey.iterrows():
    source.append(node_to_index[str(row['year'])])
    target.append(node_to_index[row['round']])
    value.append(1)  # 每个路径计为1

# 轮次 -> 类型
for _, row in df_sankey.iterrows():
    source.append(node_to_index[row['round']])
    target.append(node_to_index[row['team_type']])
    value.append(1)  # 每个路径计为1

# 创建桑基图
fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=unique_nodes,
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

fig.update_layout(
    title_text="21-25赛季NBA冠军球队夺冠路径攻防类型桑基图",
    font_size=12,
    title_x=0.5
)

# 显示图表
fig.show()

# 保存为PNG文件
fig.write_image("sankey_diagram.png", width=1000, height=600)
