import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Timeline, Grid, Line
from pyecharts.options import GraphicItem, GraphicTextStyleOpts, GraphicBasicStyleOpts
import pandas as pd


Provinces = ["北京市", "天津市", "河北省", "山西省", "内蒙古自治区", "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区", "海南省", "重庆市", "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省", "宁夏回族自治区", "新疆维吾尔自治区", "西藏"]# 自治区


# 指定文件路径和引擎
file_path = '表观碳排放清单.xlsx'
engine = 'openpyxl'

# t1 = Timeline()

# 修改 get_year_chart 函数以生成折线图
def get_year_chart(year: int):
    df = pd.read_excel(file_path, sheet_name=f'{year}', engine="openpyxl")
    data = df.iloc[4, 2:32]  # 取第5行第3到31列数据
    Values = data.tolist()

    line_chart = (
        Line()
        .add_xaxis(Provinces)
        .add_yaxis(
            series_name=f"{year}年排放量",
            y_axis=Values,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="1997~2021年中国各省二氧化碳排放量",
                subtitle="单位：公吨(mt)CO₂",
                pos_left="center",
                pos_top="top",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=25,
                ),
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-45)),
            yaxis_opts=opts.AxisOpts(name="排放量"),
        )
    )

    grid_chart = (
        Grid()
        .add(line_chart, grid_opts=opts.GridOpts())
    )

    return grid_chart





    # return map_chart




# Draw Timeline
time_list = [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
timeline = Timeline(
    init_opts=opts.InitOpts(width="1200px", height="800px", theme=ThemeType.LIGHT)
)


for y in time_list:
    g = get_year_chart(year=y)
    timeline.add(g, time_point=str(y))

timeline.add_schema(
    orient="horizontal",  # 将时间轴设置为水平方向
    is_auto_play=True,
    is_inverse=False,  # 根据需要调整逆序播放
    play_interval=5000,
    pos_left="50",  # 调整左侧位置
    pos_right="10",  # 调整右侧位置
    pos_top="690",  # 将时间轴位置放在图表下方
    pos_bottom="60", # 调整数字的底部位置
    width="1000",  # 调整时间轴的宽度以适应页面
    label_opts=opts.LabelOpts(is_show=True, color="#fff"),
)

timeline.render("3_2_1997~2021年中国各省二氧化碳排放量.html")

