import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import warnings
import datetime

warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
# 设置可显示的最大行列数量
pd.set_option('display.max_rows', 100, 'display.max_columns', 100, "display.max_colwidth", 1000, 'display.width', 1000)
# 读取数据
data = pd.read_excel("cars_info.xlsx", na_values=np.nan)
# 每列数据为空地列，数量大于80000，删除该列（无参考价值）
for c in data.columns:
    if data[c].isna().sum() > 80000:
        data.drop([c], axis=1, inplace=True)

# 每列数据为“无”的列，数量大于60000，删除该列（无参考价值）
for c in data.columns:
    if data[c].isin(["无"]).sum() > 60000:
        data.drop([c], axis=1, inplace=True)

# 因为数据本身含有长宽高的单独列，因此“长*宽*高(mm)”列删除
data.drop(['长*宽*高(mm)'], axis=1, inplace=True)

# 数据中许多列都包含“标配”，数量大于60000时无参考价值
for c in data.columns:
    if data[c].isin(["标配"]).sum() > 60000:
        print(c, data[c].isin(["标配"]).sum())
        data.drop([c], axis=1, inplace=True)

# 删除 “售价” 和 “排量” 为空的行
data.dropna(axis=0, subset=["售价", "排量(L)"], inplace=True)

# 该列含有大量范围值，且已有新车售价，删除处理
data.drop(['厂商新车指导价'], axis=1, inplace=True)

# “过户记录”许多为空，我们认为可能无过户记录，因此填充0；“载客/人”按照该列平均值进行填充
data['过户记录'].fillna(0, inplace=True)
data['载客/人'].fillna(int(data['载客/人'].mean()), inplace=True)

# 筛选出可以转化为数值型数据的列
numerical_col = ['售价', '新车售价', '行驶里程', '过户记录',
                 '载客/人', '排量(L)', '最高车速(km/h)', '官方0-100km/h加速(s)',
                 '工信部综合油耗(L/100km)', '长度(mm)', '宽度(mm)', '高度(mm)',
                 '轴距(mm)', '前轮距(mm)', '后轮距(mm)', '车门数', '油箱容积(L)',
                 '整备质量(kg)', '最小离地间隙(mm)', '排量(mL)', '气缸数(个)',
                 '每缸气门数(个)', '压缩比', '最大马力(Ps)', '最大功率(kW)',
                 '最大扭矩(N·m)'
                 ]
numerical_df = data[numerical_col]

# 将非数值型数据替换为np.nan
for c in numerical_col[5:]:
    numerical_df[c] = numerical_df[c].replace("无", np.nan).replace("false", np.nan).replace("未知", np.nan)

# 空值填充
mean_fill_col = ['排量(L)', '最高车速(km/h)', '官方0-100km/h加速(s)',
                 '工信部综合油耗(L/100km)', '长度(mm)', '宽度(mm)', '高度(mm)',
                 '轴距(mm)', '前轮距(mm)', '后轮距(mm)', '油箱容积(L)',
                 '整备质量(kg)', '最小离地间隙(mm)', '排量(mL)', '压缩比',
                 '最大马力(Ps)', '最大功率(kW)', '最大扭矩(N·m)'
                 ]
many_fill_col = ['车门数', '气缸数(个)', '每缸气门数(个)']  # 多数都为4

# 将dataframe转化成float类型
numerical_df = numerical_df.astype(float)

# 进行填充
for c in mean_fill_col:
    numerical_df[c].fillna(numerical_df[c].mean(), inplace=True)

for c in many_fill_col:
    numerical_df[c].fillna(4, inplace=True)

# 将处理完的数据更新至data中
data[numerical_col] = numerical_df


# 处理 ['座位数', '行李厢容积(L)', '最大功率转速(rpm)', '最大扭矩转速(rpm)'] 中的异常值
# 异常值处理函数
def picknum(df, c):
    if '-' in df[c]:
        num_list = df[c].split('-')
        return num_list[0]
    elif '―' in df[c]:
        num_list = df[c].split('―')
        return num_list[0]
    elif '～' in df[c]:
        num_list = df[c].split('～')
        return num_list[0]
    elif '/' in df[c]:
        num_list = df[c].split('/')
        return num_list[0]
    else:
        return df[c]


picknum_col = ['座位数', '行李厢容积(L)', '最大功率转速(rpm)', '最大扭矩转速(rpm)']

# 转化为str类型
data[picknum_col] = data[picknum_col].astype(str)

# 异常值处理
for c in picknum_col:
    data[c] = data.apply(lambda x: picknum(x, c), axis=1)

# 将“无”、“false”、“未知” 等数据替换为空
for c in picknum_col:
    data[c] = data[c].replace("无", np.nan).replace("false", np.nan).replace("未知", np.nan)

data[picknum_col] = data[picknum_col].astype(float)

# 众数填充
data['座位数'].fillna(5, inplace=True)

# 均值填充
for c in picknum_col[1:]:
    data[c].fillna(data[c].mean(), inplace=True)

# 处理日期型数据
date_col = ['商业险过期日期', '交强险过期日期', '注册日期', '出厂日期', '车船税过期日期']

data['数据获取日期'] = '2020-07-25'

date_col.append('数据获取日期')


# 处理日期型数据函数
def caldate(df, c):
    if pd.isnull(df['出厂日期']):
        return np.nan
    else:
        d1 = datetime.datetime.strptime('2020-07-25', "%Y-%m-%d")
        d2 = datetime.datetime.strptime(df[c], "%Y-%m-%d")
        diff_days = d1 - d2
        # print(diff_days)
        return diff_days.days


# 处理数据中的异常值
for c in date_col[:-1]:
    data[c] = data[c].replace("--", np.nan)

# 生成时间差的列
for c in date_col[:-1]:
    data[c + '差（天）'] = data.apply(lambda x: caldate(x, c), axis=1)

new_date_col = ['商业险过期日期差（天）', '交强险过期日期差（天）', '注册日期差（天）', '出厂日期差（天）',
                '车船税过期日期差（天）']

# 均值填充
for c in new_date_col:
    data[c].fillna(data[c].mean(), inplace=True)

# 删除之前的日期列
data.drop(date_col, axis=1, inplace=True)
# 处理0-1型数据
zero_one_col_names = ['前排侧气囊', '无钥匙启动系统', 'TRC牵引力控制系统', '上坡辅助', '电动天窗',
                      '真皮方向盘', '日间行车灯', '自动头灯', '后视镜加热', '后雨刷', '后座出风口',
                      '4S店保养', '原始购车/过户发票', '车辆购置税完税证明']

# 异常值替换及空值填充
for c in zero_one_col_names:
    data[c] = data[c].replace("无", 0).replace("false", 0).replace("true", 1).replace("标配", 1).replace("false",
                                                                                                         0).replace(
        "否", 0).replace("是", 1).replace("有（已见发票）", 1).replace("有（未见发票）", 0).replace("已缴税（未见证明）",
                                                                                                0).replace(
        "已缴税（已见证明）", 1).replace("K请问欺负我测了没人粉粉嫩嫩妇女。。佛方法v。。", 0)
    data[c].fillna(0, inplace=True)
one_hot_col_names = ['进气形式', '气缸排列形式', '配气机构', '燃油标号', '供油方式', '缸盖材料',
                     '缸体材料', '燃油形式', '变速箱类型', '驱动方式', '助力类型', '车体结构',
                     '前制动', '后制动', '驻车制动类型', '备胎规格', '定速巡航', '真皮座椅',
                     '变速器类型', '燃料类型', '车身颜色', '挡位个数']

# 这些是在excel筛选时发现的一些异常值，进行替换
data['挡位个数'] = data['挡位个数'].replace("无", "无级变速")
data['车身颜色'] = data['车身颜色'].replace("--", np.nan)
data['真皮座椅'] = data['真皮座椅'].replace("，", np.nan)
data['定速巡航'] = data['定速巡航'].replace("/", np.nan).replace("田......看", np.nan)
data['助力类型'] = data['助力类型'].replace("无助力", "无")

for c in one_hot_col_names:
    data[c] = data[c].replace("false", "无")
    data[c].fillna("无", inplace=True)

# 使用pandas中的get_dummies方法，直接将想要转换成独热编码额数据进行转换
one_hot_data = pd.get_dummies(data[one_hot_col_names])

# 合并独热编码数据，并删除之前的列
data = pd.concat([data, one_hot_data], axis=1)


# 获取当前数据类型为数值型的列
final_col = list(data.describe().columns)
final_data = data[final_col]
# 添加回原数据集中需要保留的列
keep_cols = ['车牌所在地', '厂商', '变速箱', '燃油形式']
final_data = pd.concat([final_data, data[keep_cols]], axis=1)

# 有22列数据形式较为复杂，在这里就不进行处理了
# 有兴趣的同学可以自己尝试进行处理

# 保存处理后的数据
final_data.to_excel("final_data.xlsx", index=False)
