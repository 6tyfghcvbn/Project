from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.commons.utils import JsCode

Provinces = ["宁夏回族自治区", "河南省", "北京市", "河北省", "辽宁省", "江西省", "上海市", "安徽省", "江苏省", "湖南省", "浙江省", "海南省", "广东省", "湖北省", "黑龙江省", "陕西省", "四川省", "内蒙古自治区", "重庆市", "广西壮族自治区", "云南省", "贵州省", "吉林省", "山西省", "山东省", "福建省", "青海省", "天津市", "新疆维吾尔自治区", "内蒙古自治区", "甘肃省", "台湾省", "山西省", "西藏自治区"]
Values = [22.8, 176.5, 69.1, 171.5, 93.6, 70.7, 74.4, 106.5, 219.3, 115.9, 178.9, 21.1, 306.1, 171.5, 60.6, 74.1, 143.3, 66.1, 69.3, 76.8, 83.5, 59.6, 52.1, 79.6, 252.5, 99.3, 18.9, 41.1, 50.7, 60.6, 43.3, 84.5, 79.6, 11.6,]

c = (
    Map()
    .add(
        series_name="",
        data_pair=[list(z) for z in zip(Provinces, Values)],
        label_opts=opts.LabelOpts(is_show=False),
        is_map_symbol_show=False,
        itemstyle_opts={
            "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
            "emphasis": {
                "areaColor": "rgba(255,255,255, 0.5)",
            },
        },
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="",
            subtitle="",
            pos_left="center",
            pos_top="top",
            title_textstyle_opts=opts.TextStyleOpts(
                font_size=25, color="rgba(255,255,255, 0.9)"
            ),
        ),
        tooltip_opts=opts.TooltipOpts(
            is_show=False,
            formatter=JsCode(
                """function(params) {
                if ('value' in params.data) {
                    return params.data.value[2] + ': ' + params.data.value[0];
                }
            }"""
            ),
        ),
        visualmap_opts=opts.VisualMapOpts(
            is_calculable=True,
            dimension=0,
            pos_left="10",
            pos_top="center",
            range_text=["High", "Low"],
            range_color=["lightskyblue", "yellow", "orangered", "red"],
            textstyle_opts=opts.TextStyleOpts(color="#ddd"),
            min_=306.1,
            max_=11.6,
        ),
    )
    .render("页面图1：全国地图.html")
)
