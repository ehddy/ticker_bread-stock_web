## 테마별 종목 리스트 히트맵
import yaml
from sqlalchemy import create_engine
import pandas as pd
# import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


with open('/home/ticker_bread/python/config/db_info.yml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

engine = create_engine(
    f"postgresql://{_cfg['POSTGRES_USER']}:{_cfg['POSTGRES_PASSWORD']}@{_cfg['POSTGRES_HOST']}:{'5432'}/{_cfg['POSTGRES_DB']}"
)

qry = """
SELECT T1.종목코드 종목코드,
	T1.종목명 종목명,
	T2.시장구분 시장구분,
	T2.섹터 섹터,
	T2.업종명 업종명,
	T1.시가총액 시가총액,
	T1.거래량 거래량,
	T1.거래대금 거래량
FROM public.stock_info T1
LEFT JOIN public.stock_symbols T2
	ON T1.종목코드 = T2.종목코드
--WHERE T2.섹터 IS NOT NULL
LIMIT 50
"""

df = pd.read_sql(qry, con=engine)

##### Treemap 그리기
app = dash.Dash(__name__)

# 대시보드 레이아웃 생성
app.layout = html.Div([
    html.Label('최소값: '),
    dcc.Input(id='min-input', type='number', value=100000000),
    
    html.Label('최댓값: '),
    dcc.Input(id='max-input', type='number', value=1000000000000),

    dcc.Graph(id='treemap')
])


# 콜백 함수 정의
@app.callback(
    Output('treemap', 'figure'),
    [Input('min-input', 'value'),
     Input('max-input', 'value')]
)
def update_treemap(min_value, max_value):
    filtered_df = df[(df['시가총액'] >= min_value) & (df['시가총액'] <= max_value)]

    # path에 '섹터' 추가
    fig = px.treemap(filtered_df, path=['섹터', px.Constant('섹터'), '종목명'], values='시가총액', color='종목명')
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

    return fig

# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)
