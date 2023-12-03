import pandas as pd
import psycopg2
import psycopg2.extras as extras
from psycopg2.extras import RealDictCursor
import yaml
import numpy as np

import requests
import datetime

class Database:
    def __init__(self):
        # db 정보
        with open('/home/code/stock_git/ticker_bread-stock_web/ticker_bread/modules/db_info.yml', encoding='UTF-8') as f:
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

    def get_index_info(self, index_name, end_date):
        # 지수 정보 가져오기
        query = f'''
        SELECT keystat_name, data_value, cycle_date
        FROM economic_indicators
        WHERE keystat_name = '{index_name}' AND cycle_date <= '{end_date}'
        ORDER BY cycle_date DESC
        LIMIT 2;
        '''
        df = pd.read_sql(query, self.conn)
    
        # 계산
        if len(df) < 2:
            print('데이터가 충분하지 않습니다.')
            return None

        index_value = df.loc[0, 'data_value']
        change_amount = index_value - df.loc[1, 'data_value']
        change_rate = change_amount / df.loc[1, 'data_value'] * 100
    
        return index_value, change_rate, change_amount

# 코스피 지수 조회
db = Database()
kospi_value, kospi_rate, kospi_amount = db.get_index_info('코스피지수', '2023-12-03')
print('코스피 지수:', kospi_value)
print('코스피 증감률:', kospi_rate)
print('코스피 증감액:', kospi_amount)

# 코스닥 지수 조회
kosdaq_value, kosdaq_rate, kosdaq_amount = db.get_index_info('코스닥지수', '2023-12-03')
print('코스닥 지수:', kosdaq_value)
print('코스닥 증감률:', kosdaq_rate)
print('코스닥 증감액:', kosdaq_amount)