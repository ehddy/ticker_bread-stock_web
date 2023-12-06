import yaml
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#tb_viz 파일에서 viz 불러오기
from tb_viz import viz

with open('/home/ticker_bread/python/config/db_info.yml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

engine = create_engine(
    f"postgresql://{_cfg['POSTGRES_USER']}:{_cfg['POSTGRES_PASSWORD']}@{_cfg['POSTGRES_HOST']}:{'5432'}/{_cfg['POSTGRES_DB']}"
)

qry = """
SELECT posting_date AS date,
	source,
	COUNT(id) AS cnt
FROM public.today_finance_news
GROUP BY posting_date,
	source
"""

df = pd.read_sql(qry, con=engine)


## 시각화 샘플
viz = viz()

## line chart
# single_line_chart(data, x값, y값)
fig = viz.single_line_chart(df, 'date', 'cnt')
# multi_line_chart(data, x값, y값, 색상구분값)
fig = viz.multi_line_chart(df, 'date', 'cnt', 'source')

fig.show()