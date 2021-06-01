import requests
import json
import re
import datetime
import itertools
# % matplotlib inline

# import warnings
# warnings.filterwarnings('ignore')
# 不发出警告

# from bokeh.io import output_notebook
# output_notebook()
# 如果在notebook绘图要用的模块
from bokeh.models import Span
from bokeh.io import curdoc
from bokeh.models import Legend
from bokeh.plotting import figure, show
from bokeh.palettes import Set3
colors = itertools.cycle(Set3[12])


c = []
with open('code.txt', 'r') as f:
    for line in f:
        c.append(line.split()[0])


def get_accumulate_value(code):
    # code = "090021"
    url = 'http://fund.eastmoney.com/pingzhongdata/%s.js' % code
    r = requests.get(url)
    content = r.text

    # 正则表达式1
    pattern = r'var fS_name = "(.*)";var fS_code ='
    # name
    name = re.findall(pattern, content)[0]

    # 正则表达式2
    pattern = r'var Data_ACWorthTrend = .*var Data_grandTotal = '
    # time&value
    search = re.findall(pattern, content)[0]

    l = search.lstrip('var Data_ACWorthTrend = ')
    data = l.rstrip(';/*累计收益率走势*/var Data_grandTotal = ')
    null = 1
    data = eval(data)
    t = []
    v = []
    for i in range(len(data)):
        data[i][0] /= 1000
        t.append(datetime.datetime.fromtimestamp(data[i][0]))
        v.append(data[i][1])
    return name, t, v


def scaled_value(t, v, period):
    yyyy = int(period[0:4])
    mm = int(period[4:6])
    dd = int(period[6:8])
    start = datetime.datetime(yyyy, mm, dd)
    if start in t:
        return t[t.index(start):], [x/v[t.index(start)] for x in v[t.index(start):]]

    else:
        return t, [x/v[0] for x in v]


curdoc().theme = 'dark_minimal'
p = figure(x_axis_type="datetime", plot_width=1920, plot_height=1500)
p.add_layout(Legend(), 'right')
for ci, co in zip(c, colors):
    n, t, v = get_accumulate_value(ci)
    t, v = scaled_value(t, v, '20210506')  # 是否从某一天开始缩放，要写开盘日，非开盘日则为所有数据
    p.line(t, v, legend_label=n, muted_color='gray', muted_alpha=0.2, color=co)
p.legend.click_policy = 'mute'
# p.legend.location = 'top_left'
p.legend.label_text_font_size = '10px'
base = Span(location=1, line_color='white')
p.renderers.extend([base])
p.xaxis.major_label_text_font_size = '18px'
p.yaxis.major_label_text_font_size = '18px'
show(p)
