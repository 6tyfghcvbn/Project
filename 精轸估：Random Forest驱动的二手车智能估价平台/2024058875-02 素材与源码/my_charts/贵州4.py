from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.commons.utils import JsCode

# y轴的值
x_data = ["法系", "欧系", "韩系", "美系", "日系", "德系", "中系"]
new_data = ["1412", "5482", "5193", "24462", "52228", "90742", "250260"]
# second_data = ["5302", "13372", "15203", "73661", "154641", "225562", "618257"]
c = (
    Bar()
    .add_xaxis(x_data)
    .add_yaxis("", new_data, label_opts=opts.LabelOpts(position="right"))
    # .add_yaxis("二手车", second_data, label_opts=opts.LabelOpts(position="right"))
    .reversal_axis()
.set_global_opts(
        title_opts=opts.TitleOpts(title="车系销量", subtitle=""),  # 这里是副标题
        brush_opts=opts.BrushOpts(),
    )
.set_series_opts(  # 自定义图表样式
        itemstyle_opts={
            "normal": {
                "color": JsCode(
                    """new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0,color: 'rgba(0, 244, 255, 1)'}, 
                    {offset: 1,color: 'rgba(0, 77, 167, 1)'}], false)"""
                ),
                "barBorderRadius": [0, 25, 25, 0], "shadowColor": "rgb(0, 160, 221)",
            }
        }
    )
    .render("贵州4.html")
)