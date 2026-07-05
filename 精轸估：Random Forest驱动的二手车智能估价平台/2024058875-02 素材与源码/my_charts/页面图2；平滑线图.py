# 平滑曲线图
import pyecharts.options as opts
from pyecharts.charts import Line

x_data = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
# 新车
y_data1 = [17509.080, 17927.997, 19699.956, 21108.678, 24292.239, 24744.020, 23671.529, 21432.872, 20063.587, 21752.529, 23088.660, 30094.000]
# 二手车
y_data2 = [4791.400, 5200.000, 6052.900, 9417.100, 7392.000, 12400.000, 13820.000, 14920.000, 14341.400, 17585.100, 16027.800, 23850.000]

(
    Line()
    .set_global_opts(
        tooltip_opts=opts.TooltipOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(type_="category"),
        yaxis_opts=opts.AxisOpts(
            name="单位（千）",
            type_="value",
            axistick_opts=opts.AxisTickOpts(is_show=True),
            splitline_opts=opts.SplitLineOpts(is_show=True),
        ),
    )
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(
        series_name="新车",
        y_axis=y_data1,
        symbol="emptyCircle",
        is_symbol_show=True,
        is_smooth=True,
        linestyle_opts="blue",
        label_opts=opts.LabelOpts(is_show=False),
    )
    .add_yaxis(
        series_name="二车车",
        y_axis=y_data2,
        symbol="emptyCircle",
        is_symbol_show=True,
        is_smooth=True,
        linestyle_opts="yellow",
        label_opts=opts.LabelOpts(is_show=False),
    )
    .render("页面图2：平滑线图.html")
)

