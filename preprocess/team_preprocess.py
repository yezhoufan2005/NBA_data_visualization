import pandas as pd
import numpy as np

# 读取数据文件
file_path ="../raw_data/TeamStatistics.csv"
df_raw = pd.read_csv(file_path, encoding="utf-8", low_memory=False)

# 检查数据形状和列名
print(f"原始数据形状: {df_raw.shape}")
print(f"原始数据列名: {df_raw.columns.tolist()}")

# 将日期列转换为datetime类型
df_raw['gameDateTimeEst'] = pd.to_datetime(df_raw['gameDateTimeEst'], format='mixed', utc=True)

# 定义标签字段
label_fields = [
    "gameId",           # 比赛ID
    "gameDateTimeEst",  # 比赛日期
    "teamId",           # 球队ID
    "opponentTeamId",   # 对手ID
    "win",              # 是否获胜
    "numMinutes",       # 比赛时间
    "teamScore",        # 球队得分
]
# 定义进攻指标
offense_fields = [
    "fieldGoalsAttempted",      # 投篮出手数
    "fieldGoalsMade",           # 投篮命中数
    "fieldGoalsPercentage",     # 投篮命中率
    "threePointersAttempted",   # 三分出手数
    "threePointersMade",        # 三分命中数
    "threePointersPercentage",  # 三分命中率
    "freeThrowsAttempted",      # 罚球出手数
    "freeThrowsMade",           # 罚球命中数
    "freeThrowsPercentage",     # 罚球命中率
    "assists",                  # 助攻
    "turnovers",                # 失误
    "reboundsOffensive",        # 进攻篮板
]
# 定义防守指标
defense_fields = [
    "blocks",           # 盖帽
    "steals",           # 抢断
    "foulsPersonal",    # 个人犯规
    "reboundsDefensive",# 防守篮板
]

# 筛选数据
# 筛选核心字段
core_fields = label_fields + offense_fields + defense_fields
df_core = df_raw[core_fields].copy()
# 筛选2021年以来的数据
df_team = df_core[df_core['gameDateTimeEst'].dt.year >= 2021].copy()
# 读取已处理的常规赛和季后赛数据
regularseason_path ="../data/Game_regularseason_2021-2025.csv"
postseason_path ="../data/Game_postseason_2021-2025.csv"
df_regular = pd.read_csv(regularseason_path, encoding="utf-8")
df_postseason = pd.read_csv(postseason_path, encoding="utf-8")
# 合并两个数据中的gameId
valid_game_ids = set(df_regular['gameId'].tolist() + df_postseason['gameId'].tolist())
# 只保留常规赛或季后赛数据
df_team = df_team[df_team['gameId'].isin(valid_game_ids)]
# 展示筛选情况
print(f"筛选后数据形状: {df_team.shape}")
print(f"实际使用的列: {df_team.columns.tolist()}")

# 处理缺失值
# 数值字段用中位数填充
numeric_columns = offense_fields + defense_fields
for col in numeric_columns:
    if col in df_team.columns:
        df_team[col] = df_team[col].fillna(df_team[col].median())
# 处理分类变量
df_team['win'] = df_team['win'].fillna(df_team['win'].mode()[0] if not df_team['win'].mode().empty else 0)

# 处理异常值
# 确保得分为非负数
df_team = df_team[df_team['teamScore'] >= 0]
# 确保命中率在合理范围内
df_team = df_team[(df_team['fieldGoalsPercentage'] >= 0) & (df_team['fieldGoalsPercentage'] <= 1)]
df_team = df_team[(df_team['threePointersPercentage'] >= 0) & (df_team['threePointersPercentage'] <= 1)]
df_team = df_team[(df_team['freeThrowsPercentage'] >= 0) & (df_team['freeThrowsPercentage'] <= 1)]

# 保存清洗后的球队统计数据
output_path ="../data/TeamStatistics_2021-2025.csv"
df_team.to_csv(output_path, index=False, encoding="utf-8")
print(f"数据预处理完成，共处理 {len(df_team)} 条记录")
