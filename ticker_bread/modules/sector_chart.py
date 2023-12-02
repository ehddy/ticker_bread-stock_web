## 테마별 종목 리스트 히트맵
import pandas as pd
# import numpy as np
import plotly.express as px

df = px.data.tips()

fig = px.icicle(
    df,
    path = ['day', 'time'],
    values = "total_bill"
)

fig.update_traces(root_color = "lightgrey")
# fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.show()

# fig.show()