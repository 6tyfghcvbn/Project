import pyecharts.options as opts
from pyecharts.charts import Pie

outer_x_data = ["最大马力(Ps)", "注册日期差(天)", "最大扭矩(N.m)", "最大功率(KW)", "行驶里程", "出厂日期差(天)", "厂商", "最高车速(km/h)", "变速箱", "新车售价"]
outer_y_data = [8.560670158, 7.354966928, 6.644153385, 5.219434439, 5.028393557, 2.476106593, 1.673368785, 0.8390688253, 0.7462096824, 52.67318612]
outer_data_pair = [list(z) for z in zip(outer_x_data, outer_y_data)]

(
    Pie()
    .add(
        series_name=" ",
        radius=["40%", "55%"],
        data_pair=outer_data_pair,
        label_opts=opts.LabelOpts(
            is_show=True,
            position="outside",
            formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}",
            background_color="#FFFFFF",#eee
            border_color="",#aaa
            border_width=1,
            border_radius=4,
            rich={
                "a": {"color": "", "lineHeight": 10},#999
                "b": {"fontSize": 16, "lineHeight": 13},
                "per": {
                    "color": "#eee",   # 16.11的字体颜色
                    "backgroundColor": "#334455",  # 16.11的背景颜色
                    "padding": [2, 4],
                    "borderRadius": 2,
                },

            },
        ),
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="",))
    .set_series_opts(
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            formatter="{a} <br/>{b}: {c} ({d}%)"
        )
    )
    .render("页面图11.html")
)
