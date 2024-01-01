import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import yfinance as yf
import psycopg2
import yaml
import requests as rq
from bs4 import BeautifulSoup as bs

class Indicators:
    def __init__(self, symbol):
        self.symbol = symbol
        with open('../../../config/db_info.yml', encoding='UTF-8') as f:
            _cfg = yaml.load(f, Loader=yaml.FullLoader)

        # PostgreSQL 연결 정보
        self.conn_info = {
            "host": _cfg['POSTGRES_HOST'],
            "database": _cfg['POSTGRES_DB'],
            "port":"5432",
            "user": _cfg['POSTGRES_USER'],
            "password": _cfg['POSTGRES_PASSWORD']
        }

        # PostgreSQL 연결
        self.conn = psycopg2.connect(**self.conn_info)
        self.recent_date = self.get_recent_date()
        self.data = self.get_data()

    # 최근 날짜 가져오기
    def get_recent_date(self):
        url = 'https://finance.naver.com/sise/'
        res = rq.get(url)
        html = bs(res.content, 'html.parser')
        recent_date = html.select_one('#time3').text.strip().split('장')[0].replace('.', '')
        recent_date = recent_date[:4] + '/' + recent_date[4:6] + '/' + recent_date[6:8]
        return recent_date

    # 지정된 종목의 데이터 가져오기
    def get_data(self):
        try:
            df = fdr.DataReader(self.symbol, end=self.recent_date)
        except:
            df = yf.download(self.symbol, end=self.recent_date)
        df['ChangeAmount'] = df['Close'].diff()
        df['Change'] = df['Close'].pct_change(fill_method=None)
        return df

    # 최근 장 마감일 기준 값, 증감률, 증감액 가져오기
    def get_recent_data(self):
        recent_data = self.data.iloc[-1][['Close', 'Change', 'ChangeAmount']].to_frame().T
        recent_data['Change'] = recent_data['Change'].apply(lambda x: str(round(x * 100, 2)) + '%')
        recent_data['ChangeAmount'] = recent_data['ChangeAmount'].apply(lambda x: str(round(x*-1, 2)) if str(x)[0] == '-' else str(round(x, 2)))
        return recent_data

    # 시계열 데이터프레임 리턴 (시작 날짜, 빈도 지정) - 장기적 추세 / 다양한 시간 단위 분석
    def get_index_data_over_time(self, start_date, freq='D'): # 'D'(일별), 'W'(주별), 'M'(월별), 'Y'(연별) 
        df = fdr.DataReader(self.symbol, start_date, self.recent_date)
        df = df.asfreq(freq, method='pad')
        return df[['Close']]
    
    # 최근 30일간의 데이터 가져오기 - 단기 추세 분석 / 최근 주가 변동 확인
    def get_last_30_days_data(self):
        start_date = (datetime.strptime(self.recent_date, "%Y/%m/%d") - timedelta(days=30)).strftime("%Y-%m-%d")
        last_30_days_data = self.data.loc[start_date:self.recent_date]['Close']
        return last_30_days_data

    # 코스피, 코스닥 상승 종목 수, 하락 종목 수 호출
    def get_up_down_count(self, index):
        cur = self.conn.cursor()

        # stock_info 테이블에서 KOSPI/KOSDAQ 등락률 파악 (기준일=recent_date일 때)
        cur.execute(f"""
            SELECT COUNT(*) FILTER (WHERE 등락률 > 0) AS up_count,
                COUNT(*) FILTER (WHERE 등락률 < 0) AS down_count
            FROM stock_info
            WHERE 시장구분 = '{index}' AND TO_CHAR(기준일, 'YYYY-MM-DD') = '{self.recent_date.replace("/", "-")}'
        """)

        up_count, down_count = cur.fetchone()

        result = pd.DataFrame({
            '상승 종목 수': [up_count],
            '하락 종목 수': [down_count]
        })

        return result

# symbols : 
# 코스피: KS11
# 코스닥: KQ11
# 나스닥 종합: IXIC
# S&P500: SPY (S&P 500 ETF) **확인 필요 (단위)
# 다우존스: DJI
# 나스닥100: NDX
# 환율 (달러/원): USD/KRW
# 금: GC=F (Comex 금)
# 원자재: ^CRB (CRB 원자재 지수)
# 엔화 (엔/원): JPY/KRW **확인 필요 (단위)
# 유가: CL=F (WTI 원유)

# Indicators = Indicators('KS11') 

# recent_data = indicators.get_recent_data()
# df = indicators.get_index_data_over_time('2020-01-01', 'D')
# last_30_days_data = indicators.get_last_30_days_data()
# up_down_count = indicators.get_up_down_count('KOSPI')

# print(recent_data)
# print(last_30_days_data)
# print(up_down_count)