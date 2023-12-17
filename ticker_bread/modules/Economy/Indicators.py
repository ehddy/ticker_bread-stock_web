import pandas as pd
import yaml
import psycopg2
import requests as rq
from bs4 import BeautifulSoup as bs
import FinanceDataReader as fdr

class Indicators:
    def __init__(self):
        # db 정보
        with open('/home/code/stock_git/ticker_bread-stock_web/config/db_info.yml', encoding='UTF-8') as f:
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

    # 최근 장 마감일자 불러오기
    def get_recent_date(self):
        url = 'https://finance.naver.com/sise/'
        res = rq.get(url)
        html = bs(res.content, 'html.parser')
        recent_date = html.select_one('#time3').text.strip().split('장')[0].replace('.', '')
        recent_date = recent_date[:4] + '/' + recent_date[4:6] + '/' + recent_date[6:8]
        return recent_date

    # 최근 장 마감일자 기준 코스피, 코스닥 정보 호출 (지수, 증감률, 증감액)
    def get_recent_index_data(self, index):
        df = fdr.DataReader(index, end=self.recent_date)
        df['ChangeAmount'] = df['Close'].diff()
        recent_data = df.iloc[-1][['Close', 'Change', 'ChangeAmount']].to_frame().T
        # 증감률을 퍼센트로 변환하고 부호, '%' 추가
        recent_data['Change'] = recent_data['Change'].apply(lambda x: str(round(x * 100, 2)) + '%')
        # 증감액에 부호 추가하고 소수점 둘째자리까지 표시
        recent_data['ChangeAmount'] = recent_data['ChangeAmount'].apply(lambda x: str(round(x*-1, 2)) if str(x)[0] == '-' else str(round(x, 2)))
        return recent_data

    # 코스피, 코스닥 지표 시계열 데이터프레임 리턴
    def get_index_data_over_time(self, index, start_date, freq='D'): # 'D'(일별), 'W'(주별), 'M'(월별), 'Y'(연별) 
        df = fdr.DataReader(index, start_date, self.recent_date)
        df = df.asfreq(freq, method='pad')
        return df[['Close']]
    
    # 코스피, 코스닥 상승 종목 수, 하락 종목 수 호출
    def get_up_down_count(self, index):
        # PostgreSQL 커서 생성
        cur = self.conn.cursor()

        # stock_info, stock_symbols 테이블 join, KOSPI/KOSDAQ 등락률 얻기 (기준일=recent_date일 때)
        cur.execute(f"""
            SELECT s.종목코드, i.등락률
            FROM stock_symbols AS s
            JOIN stock_info AS i
            ON s.종목코드 = i.종목코드
            WHERE s.시장구분 = '{index}' AND TO_CHAR(i.기준일, 'YYYY/MM/DD') = '{self.recent_date}'
        """)

        # 등락률이 0보다 크면 상승, 작으면 하락으로 분류
        up_count = 0
        down_count = 0
        for _, change in cur.fetchall():
            if change > 0:
                up_count += 1
            elif change < 0:
                down_count += 1
                
        result = pd.DataFrame({
            '상승 종목 수': [up_count],
            '하락 종목 수': [down_count]
        })

        return result


# indicators = Indicators() # Indicators 인스턴스 생성

# recent_kospi_df = indicators.get_recent_index_data('KS11')
# recent_kosdaq_df = indicators.get_recent_index_data('KQ11')
# print(recent_kospi_df)
# print(recent_kosdaq_df)

# kospi_time_series_df = indicators.get_index_data_over_time('KS11', '2023-01-01', 'D')
# kosdaq_time_series_df = indicators.get_index_data_over_time('KQ11', '2023-01-01', 'D')
# print(kospi_time_series_df)
# print(kosdaq_time_series_df)

# kospi_updown_df = indicators.get_up_down_count('KOSPI')
# kosdaq_updown_df = indicators.get_up_down_count('KOSDAQ') 
# print(kospi_updown_df)
# print(kosdaq_updown_df)
