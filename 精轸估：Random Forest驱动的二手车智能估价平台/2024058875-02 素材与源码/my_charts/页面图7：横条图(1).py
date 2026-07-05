from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.faker import Faker

# y轴的值
x_data = ["法系", "欧系", "韩系", "美系", "日系", "德系", "中系"]
new_data = ["5302", "13372", "15203", "73661", "154641", "225562", "618257"]
second_data = ["5302", "13372", "15203", "73661", "154641", "225562", "618257"]
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
    .render("页面图7：横条图.html")
)