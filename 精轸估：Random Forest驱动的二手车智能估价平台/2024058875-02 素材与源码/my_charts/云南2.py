import pyecharts.options as opts
from pyecharts.charts import Funnel

x_data = ["长安汽车", "上汽通用五菱", "吉利汽车", "奇瑞汽车", "一汽大众"]  # {b}
y_data = [20, 40, 60, 80, 100]    # {c}

data = [[x_data[i], y_data[i]] for i in range(len(x_data))]

(
    Funnel()
    .add(
        series_name="厂商",  # {a}
        data_pair=data,
        sort_="ascending",
        gap=2,   # 漏斗图中各项之间的间距。数字越大，间距越大。
        tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b}"),
        label_opts=opts.LabelOpts(is_show=True, position="inside"),
        itemstyle_opts=opts.ItemStyleOpts(border_color="#fff", border_width=1),
    )
    .set_global_opts(title_opts=opts.TitleOpts(title=" ", subtitle=" "))    # 漏斗图  纯属虚构
    .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    .render("云南2.html")
)