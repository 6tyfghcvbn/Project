import pyecharts.options as opts
from pyecharts.charts import Pie


inner_x_data = ["传统能源", "新能源"]
inner_y_data = [728348, 377654]
inner_data_pair = [list(z) for z in zip(inner_x_data, inner_y_data)]

outer_x_data = ["华中", "华北", "华南", "华东", "西南", "西北", "东北"]
outer_y_data = [193666, 136958, 110020, 354511, 178213, 77323, 55271]
outer_data_pair = [list(z) for z in zip(outer_x_data, outer_y_data)]

(
    Pie()
    .add(
        series_name="占比",
        data_pair=inner_data_pair,
        radius=[0, "30%"],
        label_opts=opts.LabelOpts(position="inner"),
    )
    .add(
        series_name=" ",
        radius=["40%", "55%"],
        data_pair=outer_data_pair,
        label_opts=opts.LabelOpts(
            position="outside",
            formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}",
            background_color="",#eee
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
    .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    .set_series_opts(
        tooltip_opts=opts.TooltipOpts(
            trigger="item",
            formatter="{a} <br/>{b}: {c} ({d}%)"
        )
    )
    .render("页面图5：环中环.html")
)
