from pyecharts import options as opts
from pyecharts.charts import Pie

x_data = ["轿车", "SUV", "MPV", "跑车"]
y_data = [10434, 11980, 1481, 26]

data3 = [[x_data[i], y_data[i]] for i in range(len(x_data))]


c = (
    Pie()
    .add(
        series_name="销量(辆)",
        data_pair=data3,
        radius=["35%", "65%"],
        center=["50%", "50%"],
        rosetype="radius",
        label_opts=opts.LabelOpts(
            is_show=True,
            position="inner"

        ),
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="汽车类型销量"),
                     legend_opts=opts.LegendOpts(is_show=False)
                     )
    .render("辽宁3.html")
)