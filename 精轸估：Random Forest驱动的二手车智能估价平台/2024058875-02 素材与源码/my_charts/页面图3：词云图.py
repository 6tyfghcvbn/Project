import pyecharts.options as opts
from pyecharts.charts import WordCloud

# 省略部分数据
# 时间是2024
data = [
    ("小米SU7", "2820103"),
    ("阿维塔", "367147"),
    ("ZEEKR001", "323411"),
    ("高山DHT-PHEV", "295856"),
    ("智界S7", "144848"),
    ("Model3", "140723"),
    ("问界M9", "113443"),
    ("ModelS", "101079"),
    ("蔚来ES6", "92345"),
    ("ZEEKR007", "88748"),
    ("Taycan", "78705"),
    ("腾势N7", "74789"),
    ("埃尔法", "72127"),
    ("理想MEGA", "71060"),
    ("小鹏X9", "54175"),
    ("蔚来ET5", "53845"),
    ("风云A8", "46618"),
    ("风神L7", "38379"),
    ("豹5", "38346"),
    ("比亚迪宋L", "74096"),
    ("问界M7", "33968"),
]

(
    WordCloud()
    .add(series_name="热度呈现", data_pair=data, word_size_range=[6, 66])
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="热度呈现", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
        ),
        tooltip_opts=opts.TooltipOpts(is_show=True),
    )
    .render("页面图3：词云图.html")
)