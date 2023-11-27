import pandas as pd
import psycopg2
import psycopg2.extras as extras
from psycopg2.extras import RealDictCursor
import yaml 

import FinanceDataReader as fdr

import requests
import pandas as pd
import datetime
from postgres_code.postgres import *

class GetIndex:
    def __init__(self):
        with open('/ticker_bread/modules/eco_info.yaml', encoding='UTF-8') as f:
            _cfg = yaml.load(f, Loader=yaml.FullLoader)
    
        self.api_key = _cfg['ECO_KEY']
        self.base_url = 'http://ecos.bok.or.kr/api/KeyStatisticList/'
        self.postgres = POSTGRES_STOCK()
        
    def GetIndicator(self):
        url = f'{self.base_url}{self.api_key}/json/kr/1/100'
        response = requests.get(url)
        result = response.json()
        
        df = pd.DataFrame(result['KeyStatisticList']['row'])
        
        df['CYCLE'] = df['CYCLE'].astype(str)
        # 문자열 형태의 'CYCLE' 열을 YYYY-MM-DD 형식으로 변환 / 열의 길이에 따라 다르게 처리
        def convert_cycle(cycle):
            if len(cycle) == 4:  # year only
                return pd.to_datetime(cycle + '0101', format='%Y%m%d')
            elif 'Q' in cycle:  # quarter data
                year, quarter = cycle.split('Q')
                month = str((int(quarter) - 1) * 3 + 1).zfill(2)
                return pd.to_datetime(year + month + '01', format='%Y%m%d')
            elif len(cycle) == 6:  # year and month data
                return pd.to_datetime(cycle+'01', format='%Y%m%d')
            else:  # full date
                return pd.to_datetime(cycle, format='%Y%m%d')

        # CYCLE_DATE라는 새로운 열에 변환된 날짜 저장
        df['CYCLE_DATE'] = df['CYCLE'].apply(convert_cycle)

        df.drop('CYCLE', axis=1, inplace=True)
        
        df = df.astype({'DATA_VALUE': 'float'})
        
        return df
    
    # postgresql 저장
    def update_indicator_postgres(self):  
	    df = self.GetIndicator()

	    # 현재 날짜 가져오기
	    now = datetime.datetime.now()

	    # 디스코드 메시지에 월 정보 포함하여 전송
	    self.discord.send_message(f"Get Indicator Info for {now.year}-{now.month}")

	    self.postgres.insert_df(df, 'economic_indicators', 'keystat_name', 'cycle_date')

# 사용 예시
# indicator = GetIndicator()
# dataframe_result = indicator.GetIndicator()
# print(dataframe_result)
# print(dataframe_result['CYCLE_DATE'].unique())
# print(dataframe_result.columns)

# indicator.update_indicator_postgres()

class Database:
    def __init__(self):
        # db 정보
        with open('/ticker_bread/modules/db_info.yml', encoding='UTF-8') as f:
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

    def get_info(self, stock_name):
        # 커서 생성
        cur = self.conn.cursor()

        # SQL 쿼리 실행
        cur.execute(f"""
            SELECT stock_info.종목코드, stock_info.종목명, stock_symbols.업종명, stock_info.종가, stock_info.시가총액 
            FROM stock_symbols LEFT JOIN stock_info 
            ON stock_symbols.종목코드 = stock_info.종목코드 
            WHERE stock_info.종목명 = '{stock_name}' 
            ORDER BY stock_info.기준일 DESC 
            LIMIT 1;
        """)

        # 결과 데이터 가져오기
        rows = cur.fetchall()
        
        # 결과를 데이터프레임으로 변환
        data = {'항목명': ['종목코드','종목명', '업종', '종가', '시가총액'], '값': []}
        for row in rows:
            data['값'].extend(row)

        # '항목명'과 '값'의 길이가 일치하도록 확인
        assert len(data['항목명']) == len(data['값']), "Lengths of '항목명' and '값' must be the same."
        
        df = pd.DataFrame(data)
        return df

db = Database()
print(db.get_closing_price('AK홀딩스'))