## viz 클래스 사용법

import yaml
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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

viz = viz()

fig = viz.single_line_chart(df, 'date', 'cnt')
fig = viz.multi_line_chart(df, 'date', 'cnt', 'source')

fig.show()