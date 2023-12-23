
import pandas as pd
import psycopg2
import psycopg2.extras as extras
from psycopg2.extras import RealDictCursor
import yaml 


class StockForDB:

    def __init__(self):
         #  db 정보
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
    
    def format_number_to_unit(self, number):
        # 억 이상의 경우 억 단위로 변환
        if number >= 10**8:
            billion = int(number / 10**8)
            formatted_billion = "{:,}".format(billion)
            return f"{formatted_billion}억원"
            
        # 천만원 이상의 경우 천만원 단위로 변환
        elif number >= 10**7:
            ten_million = int(number / 10**7)
            formatted_ten_million = "{:,}".format(ten_million)
            return f"{formatted_ten_million}천만원"
        else:
            return format(number, ',')


    # 실시간(가장 최근에 저장된 데이터 기준) 등락률을 리턴 
    def get_fluctuation_stock(self, stock_type='Kospi', desc=False):

        if desc == False:
            desc_or_asc = "Top"
        else:
            desc_or_asc = "Bottom"

        # 커서 생성
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        query = f"""
            SELECT * fROM public."{stock_type}_fluctuationRate_{desc_or_asc}5"
        """

        # 쿼리 실행
        cur.execute(query)




        df = pd.DataFrame(cur.fetchall())

        # 화면에 보여주기 좋은 format으로 변경
        df['현재가'] = df["현재가"].apply(lambda x : format(x, ','))
        df['거래량'] = df["거래량"].apply(lambda x : format(x, ','))

        df['시가총액'] = df['시가총액'].apply(lambda x : self.format_number_to_unit(x))

        df['거래대금'] = df["거래대금"].apply(lambda x : self.format_number_to_unit(x))
        
        cur.close()

        return df
    
