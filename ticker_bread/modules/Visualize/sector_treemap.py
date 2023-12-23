import yaml
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


with open('/home/stock_web/config/db_info.yml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

engine = create_engine(
    f"postgresql://{_cfg['POSTGRES_USER']}:{_cfg['POSTGRES_PASSWORD']}@{_cfg['POSTGRES_HOST']}:{'5432'}/{_cfg['POSTGRES_DB']}"
)

qry = """
SELECT 종목코드 종목코드,
    종목명 종목명,
	시장구분 시장구분,
	섹터 섹터,
	업종명 업종명,
	시가총액 시가총액,
	거래량 거래량,
	거래대금 거래량
    public.stock_info T1
--WHERE T2.섹터 IS NOT NULL
--LIMIT 50
"""

df = pd.read_sql(qry, con=engine)

##### Treemap 그리기
app = dash.Dash(__name__)

# 드롭다운 옵션 생성
dropdown_options = [
    {'label': '섹터', 'value': '섹터'},
    {'label': '업종명', 'value': '업종명'},
    {'label': '시장구분', 'value': '시장구분'}
]

# 대시보드 레이아웃 생성
app.layout = html.Div([
    html.H1("example"),

    html.Div([
        dcc.Dropdown(
            id = 'dropdown',
            options = dropdown_options,
            value = '섹터',
            style = {'width': '30%', 'height': '300%'}
        ),
    ], style={'margin-bottom': '20px'}),

    html.Label('최소값: '),
    dcc.Input(id='min-input', type='number', value=500000000000),
    
    html.Label('최댓값: '),
    dcc.Input(id='max-input', type='number', value=5000000000000),

    dcc.Graph(id='treemap')
])


# 콜백 함수 정의
@app.callback(
    Output('treemap', 'figure'),
    [Input('dropdown', 'value'),
     Input('min-input', 'value'),
     Input('max-input', 'value')]
)
def update_treemap(selected_value, min_value, max_value):
    filtered_df = df[(df['시가총액'] >= min_value) & (df['시가총액'] <= max_value)]

    # parents = [''] * len(filtered_df['종목명'])

    # path에 '섹터' 추가
    # fig = px.treemap(filtered_df, path=['섹터', px.Constant('섹터'), '종목명'], values='시가총액', color='종목명')
    fig = px.treemap(filtered_df, path=[px.Constant(selected_value), selected_value, '종목명'], values='시가총액', color='시가총액',
                     color_continuous_scale='Viridis', #'RdBu'
                     color_continuous_midpoint=np.average(df['시가총액']),
                     hover_data=['종목명', selected_value, '시가총액']
                     )

    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25),
                      title=f"{selected_value} 기준 트리맵", height=600
    )

    fig.write_html("/home/ticker_bread/python/ticker_bread/modules/sector_treemap.html")

    return fig


# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)
