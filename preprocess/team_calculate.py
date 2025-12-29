import pandas as pd
import numpy as np

# 读取预处理后的数据
file_path ="../data/TeamStatistics_2021-2025.csv"
df_team = pd.read_csv(file_path, encoding="utf-8", low_memory=False)

# 删除只出现一次的gameId
game_counts = df_team['gameId'].value_counts()
games_with_two_teams = game_counts[game_counts == 2].index
df_team = df_team[df_team['gameId'].isin(games_with_two_teams)]

# 创建对手数据映射
opponent_data_map = {}
for game_id, game_data in df_team.groupby('gameId'):
    if len(game_data) == 2:
        team1 = game_data.iloc[0]
        team2 = game_data.iloc[1]
        # 将team2的数据作为team1的对手数据
        opponent_data_map[(game_id, team1['teamId'])] = team2
        # 将team1的数据作为team2的对手数据
        opponent_data_map[(game_id, team2['teamId'])] = team1

# 为DataFrame添加对手数据列
df_team['Opp_PTS'] = 0
df_team['Opp_FGA'] = 0
df_team['Opp_FGM'] = 0
df_team['Opp_FGP'] = 0.0
df_team['Opp_TPA'] = 0
df_team['Opp_TPM'] = 0
df_team['Opp_TPP'] = 0.0
df_team['Opp_FTA'] = 0
df_team['Opp_FTM'] = 0
df_team['Opp_FTP'] = 0.0
df_team['Opp_AST'] = 0
df_team['Opp_TOV'] = 0
df_team['Opp_BLK'] = 0
df_team['Opp_STL'] = 0
df_team['Opp_PF'] = 0
df_team['Opp_OREB'] = 0
df_team['Opp_DREB'] = 0

# 填充对手数据
for idx, row in df_team.iterrows():
    game_id = row['gameId']
    team_id = row['teamId']
    if (game_id, team_id) in opponent_data_map:
        opponent_row = opponent_data_map[(game_id, team_id)]
        df_team.at[idx, 'Opp_PTS'] = opponent_row['teamScore']
        df_team.at[idx, 'Opp_FGA'] = opponent_row['fieldGoalsAttempted']
        df_team.at[idx, 'Opp_FGM'] = opponent_row['fieldGoalsMade']
        df_team.at[idx, 'Opp_FGP'] = opponent_row['fieldGoalsPercentage']
        df_team.at[idx, 'Opp_TPA'] = opponent_row['threePointersAttempted']
        df_team.at[idx, 'Opp_TPM'] = opponent_row['threePointersMade']
        df_team.at[idx, 'Opp_TPP'] = opponent_row['threePointersPercentage']
        df_team.at[idx, 'Opp_FTA'] = opponent_row['freeThrowsAttempted']
        df_team.at[idx, 'Opp_FTM'] = opponent_row['freeThrowsMade']
        df_team.at[idx, 'Opp_FTP'] = opponent_row['freeThrowsPercentage']
        df_team.at[idx, 'Opp_AST'] = opponent_row['assists']
        df_team.at[idx, 'Opp_TOV'] = opponent_row['turnovers']
        df_team.at[idx, 'Opp_BLK'] = opponent_row['blocks']
        df_team.at[idx, 'Opp_STL'] = opponent_row['steals']
        df_team.at[idx, 'Opp_PF'] = opponent_row['foulsPersonal']
        df_team.at[idx, 'Opp_OREB'] = opponent_row['reboundsOffensive']
        df_team.at[idx, 'Opp_DREB'] = opponent_row['reboundsDefensive']

# 重命名现有字段为新字段名
df_team = df_team.rename(columns={
    'numMinutes': 'Min',
    'teamScore': 'PTS',
    'fieldGoalsAttempted': 'FGA',
    'fieldGoalsMade': 'FGM',
    'fieldGoalsPercentage': 'FGP',
    'threePointersAttempted': 'TPA',
    'threePointersMade': 'TPM',
    'threePointersPercentage': 'TPP',
    'freeThrowsAttempted': 'FTA',
    'freeThrowsMade': 'FTM',
    'freeThrowsPercentage': 'FTP',
    'assists': 'AST',
    'turnovers': 'TOV',
    'blocks': 'BLK',
    'steals': 'STL',
    'foulsPersonal': 'PF',
    'reboundsOffensive': 'OREB',
    'reboundsDefensive': 'DREB'
})

# 添加高级统计字段
# 添加基础字段
df_team['Poss'] = df_team['FGA'] + 0.44 * df_team['FTA'] + df_team['TOV'] - df_team['OREB']
df_team['Opp_Poss'] = df_team['Opp_FGA'] + 0.44 * df_team['Opp_FTA'] + df_team['Opp_TOV'] - df_team['Opp_OREB']
# 添加进攻字段
# 添加有效命中率
df_team['eFG'] = (df_team['FGM'] + 0.5 * df_team['TPM']) / df_team['FGA']
df_team.loc[df_team['FGA'] == 0, 'eFG'] = 0
# 添加真实命中率
df_team['TS'] = df_team['PTS'] / (2 * (df_team['FGA'] + 0.44 * df_team['FTA']))
df_team.loc[df_team['FGA'] + 0.44 * df_team['FTA'] == 0, 'TS'] = 0
# 添加助攻率
df_team['AST_Per'] = df_team['AST'] / df_team['FGM']
df_team.loc[df_team['FGM'] == 0, 'AST_Per'] = 0
# 添加失误率
df_team['TOV_Rat'] = df_team['TOV'] / df_team['Poss'] * 100
df_team.loc[df_team['Poss'] == 0, 'TOV_Rat'] = 0
# 添加进攻篮板率
df_team['OREB_Per'] = df_team['OREB'] / (df_team['OREB'] + df_team['Opp_DREB'])
df_team.loc[df_team['OREB'] + df_team['Opp_DREB'] == 0, 'OREB_Per'] = 0

# 添加防守字段
# 添加对手有效命中率
df_team['Opp_eFG'] = (df_team['Opp_FGM'] + 0.5 * df_team['Opp_TPM']) / df_team['Opp_FGA']
df_team.loc[df_team['Opp_FGA'] == 0, 'Opp_eFG'] = 0
# 添加盖帽率
df_team['BLK_Rat'] = df_team['BLK'] / df_team['Opp_Poss'] * 100
df_team.loc[df_team['Opp_Poss'] == 0, 'BLK_Rat'] = 0
# 添加抢断率
df_team['STL_Rat'] = df_team['STL'] / df_team['Opp_Poss'] * 100
df_team.loc[df_team['Opp_Poss'] == 0, 'STL_Rat'] = 0
# 添加犯规率
df_team['PF_Rat'] = df_team['PF'] / df_team['Opp_Poss'] * 100
df_team.loc[df_team['Opp_Poss'] == 0, 'PF_Rat'] = 0
# 添加对手失误率
df_team['Opp_TOV_Rat'] = df_team['Opp_TOV'] / df_team['Opp_Poss'] * 100
df_team.loc[df_team['Opp_Poss'] == 0, 'Opp_TOV_Rat'] = 0
# 添加防守篮板率
df_team['DREB_Per'] = df_team['DREB'] / (df_team['DREB'] + df_team['Opp_OREB'])
df_team.loc[df_team['DREB'] + df_team['Opp_OREB'] == 0, 'DREB_Per'] = 0

# 计算联盟平均值
league_avg_eFG = df_team['eFG'].mean()
league_avg_TS = df_team['TS'].mean()
league_avg_AST_Per = df_team['AST_Per'].mean()
league_avg_TOV_Rat = df_team['TOV_Rat'].mean()
league_avg_OREB_Per = df_team['OREB_Per'].mean()

league_avg_Opp_eFG = df_team['Opp_eFG'].mean()
league_avg_STL_Rat = df_team['STL_Rat'].mean()
league_avg_BLK_Rat = df_team['BLK_Rat'].mean()
league_avg_PF_Rat = df_team['PF_Rat'].mean()
league_avg_Opp_TOV_Rat = df_team['Opp_TOV_Rat'].mean()
league_avg_DREB_Per = df_team['DREB_Per'].mean()

# 添加综合字段
# 添加进攻效率
df_team['off_eff'] = df_team['PTS'] / df_team['Poss'] * 100
# 添加防守效率
df_team['def_eff'] = df_team['Opp_PTS'] / df_team['Opp_Poss'] * 100
# 添加净效率
df_team['net_eff'] = df_team['off_eff'] - df_team['def_eff']
# 添加进攻评分
df_team['off_rat'] = (
    0.3 * (df_team['eFG'] / league_avg_eFG * 100) +
    0.25 * (df_team['TS'] / league_avg_TS * 100) +
    0.2 * (df_team['AST_Per'] / league_avg_AST_Per * 100) +
    0.15 * ((league_avg_TOV_Rat / df_team['TOV_Rat']) * 100) + #逆向值
    0.1 * (df_team['OREB_Per'] / league_avg_OREB_Per * 100)
)
# 添加防守评分
df_team['def_rat'] = (
    0.25 * ((league_avg_Opp_eFG / df_team['Opp_eFG']) * 100) + #逆向值
    0.2 * (df_team['STL_Rat'] / league_avg_STL_Rat * 100) +
    0.2 * (df_team['BLK_Rat'] / league_avg_BLK_Rat * 100) +
    0.15 * (df_team['Opp_TOV_Rat'] / league_avg_Opp_TOV_Rat * 100) +
    0.1 * ((league_avg_PF_Rat / df_team['PF_Rat']) * 100) + #逆向值
    0.1 * (df_team['DREB_Per'] / league_avg_DREB_Per * 100)
)
# 添加攻防总评分
df_team['net_rat'] = df_team['off_rat'] + df_team['def_rat']

# 对所有高级统计字段保留最多3位有效数字
advanced_stat_columns = [
    'eFG', 'TS', 'AST_Per', 'TOV_Rat', 'OREB_Per', 'off_eff', 'off_rat',
    'Opp_eFG', 'BLK_Rat', 'STL_Rat', 'PF_Rat', 'Opp_TOV_Rat', 'DREB_Per',
    'def_eff', 'def_rat', 'net_rat', 'net_eff'
]
for col in advanced_stat_columns:
    if col in df_team.columns:
        df_team[col] = df_team[col].round(3)

print(f"添加对手数据后数据形状: {df_team.shape}")
print(f"最终使用的列: {df_team.columns.tolist()}")

# 保存更新后的数据
output_path ="../data/TeamStatisticsWithOpponent_2021-2025.csv"
df_team.to_csv(output_path, index=False, encoding="utf-8")
print(f"数据预处理完成，共处理 {len(df_team)} 条记录")
