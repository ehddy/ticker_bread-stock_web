import yaml
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


with open('/home/stock_web/config/db_info.yml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
# 데이터베이스 연결 및 데이터 로딩
def treemap():
    engine = create_engine(
    f"postgresql://{_cfg['POSTGRES_USER']}:{_cfg['POSTGRES_PASSWORD']}@{_cfg['POSTGRES_HOST']}:{'5432'}/{_cfg['POSTGRES_DB']}"
)
    qry = """
    SELECT 종목코드,
        종목명 종목명,
        시장구분,
        섹터,
        업종명,
        시가총액,
        거래량,
        거래대금
    FROM
    stock_info
    Where 
    섹터 is Not Null
    """

    df = pd.read_sql(qry, con=engine)
    
    # None 값을 'Unknown'으로 대체
    df['섹터'] = df['섹터'].fillna('None')
    df = df[df['섹터'] != 'None'].reset_index(drop=True)

    # 드롭다운 옵션 생성
    dropdown_options = [
        {'label': '섹터', 'value': '섹터'},
        {'label': '업종명', 'value': '업종명'},
        {'label': '시장구분', 'value': '시장구분'}
    ]

    # 대시보드 레이아웃 생성
    fig = px.treemap(df, path=['섹터', px.Constant('섹터'), '종목명'],
                    values='시가총액', color='시가총액',
                    color_continuous_scale='Viridis',
                    hover_data=['종목명', '섹터', '시가총액']
                    )

    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25),
                     height=600
                    )

    # HTML 파일에 그래프를 저장
    # fig.write_html("/home/stock_web/ticker_bread/templates/tree.html")
    return fig