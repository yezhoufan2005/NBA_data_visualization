import pandas as pd
import numpy as np

# 读取数据文件
file_path ="../raw_data/Games.csv"
df_raw = pd.read_csv(file_path, encoding="utf-8", low_memory=False)

# 检查数据形状和列名
print(f"原始数据形状: {df_raw.shape}")
print(f"原始数据列名: {df_raw.columns.tolist()}")

# 将日期列转换为datetime类型
df_raw['gameDateTimeEst'] = pd.to_datetime(df_raw['gameDateTimeEst'], format='mixed', utc=True)

# 定义核心字段
core_fields = [
    "gameId",            # 比赛ID
    "gameDateTimeEst",   # 比赛日期
    "hometeamCity",      # 主场球队城市
    "hometeamName",      # 主场球队名称
    "hometeamId",        # 主场球队ID
    "awayteamCity",      # 客场球队城市
    "awayteamName",      # 客场球队名称
    "awayteamId",        # 客场球队ID
    "homeScore",         # 主场得分
    "awayScore",         # 客场得分
    "winner",            # 获胜球队ID
    "gameType",          # 比赛类型
    "attendance",        # 观众人数
    "gameLabel",         # 比赛标题
    "seriesGameNumber",  # 系列赛场次
]

# 筛选数据
# 筛选核心字段
df_core = df_raw[core_fields].copy()
# 筛选常规赛数据和空值
df_regularseason = df_core[df_core['gameType'].isin(['Regular Season']) | df_core['gameType'].isna()].copy()
# 将空值赋值为'Regular Season'
df_regularseason['gameType'] = df_regularseason['gameType'].fillna('Regular Season')
# 筛选2021年以来的数据
df_regularseason = df_regularseason[df_regularseason['gameDateTimeEst'].dt.year >= 2021].copy()
# 展示筛选情况
print(f"筛选后数据形状: {df_core.shape}")
print(f"实际使用的列: {df_core.columns.tolist()}")

# 处理缺失值
# 数值字段用中位数填充
df_regularseason['homeScore'] = df_regularseason['homeScore'].fillna(df_regularseason['homeScore'].median())
df_regularseason['awayScore'] = df_regularseason['awayScore'].fillna(df_regularseason['awayScore'].median())
df_regularseason['attendance'] = df_regularseason['attendance'].fillna(df_regularseason['attendance'].median())
# 主场球队字段组
home_team_fields = ['hometeamCity', 'hometeamName', 'hometeamId']
# 客场球队字段组
away_team_fields = ['awayteamCity', 'awayteamName', 'awayteamId']
# 字段按球队分组进行锁定匹配填充
def fill_team_fields(df, team_fields):
    for i, field in enumerate(team_fields):
        mode_val = df[field].mode()
        if not mode_val.empty:
            df[field] = df[field].fillna(mode_val[0])
        else:
            df[field] = df[field].fillna('Unknown')
    return df
df_regularseason = fill_team_fields(df_regularseason, home_team_fields)
df_regularseason = fill_team_fields(df_regularseason, away_team_fields)

# 处理异常值
# 确保得分范围合理
df_regularseason = df_regularseason[(df_regularseason['homeScore'] >= 0) & (df_regularseason['homeScore'] <= 200)]
df_regularseason = df_regularseason[(df_regularseason['awayScore'] >= 0) & (df_regularseason['awayScore'] <= 200)]
# 确保观众人数合理
df_regularseason = df_regularseason[(df_regularseason['attendance'] >= 0) & (df_regularseason['attendance'] <= 100000)]
# 确保主客场球队不相同
df_regularseason = df_regularseason[df_regularseason['hometeamId'] != df_regularseason['awayteamId']]
# 确保主客场得分不相同
df_regularseason = df_regularseason[df_regularseason["homeScore"] != df_regularseason["awayScore"]]
# 将比赛标题和系列赛场次设置为空值
df_regularseason['gameLabel'] = None
df_regularseason['seriesGameNumber'] = None

# 添加字段
# 添加总分
df_regularseason['totalScore'] = df_regularseason['homeScore'] + df_regularseason['awayScore']
# 添加分差
df_regularseason['scoreDifference'] = abs(df_regularseason['homeScore'] - df_regularseason['awayScore'])

# 保存清洗后的常规赛数据
output_path ="../data/Game_regularseason_2021-2025.csv"
df_regularseason.to_csv(output_path, index=False, encoding="utf-8")
print(f"数据预处理完成，共处理 {len(df_core)} 条记录")
