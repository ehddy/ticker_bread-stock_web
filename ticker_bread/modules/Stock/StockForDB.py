
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
    def get_top(self, stock_type, desc=False):
        # 커서 생성
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        if desc == True:
            asc_or_desc = "DESC"
        else:
            asc_or_desc = "ASC"
        # 쿼리문
        query = f"""
        select T1.종목명, T1.종가 as 현재가, T1.등락률, T1.시가총액, 
        T1.거래량, T1.거래대금, T1.기준일
        from stock_info T1
        LEFT JOIN public.stock_symbols T2
            ON T1.종목코드 = T2.종목코드
        WHERE T2.시장구분= '{stock_type}'
        ORDER BY T1.기준일 DESC, 등락률 {asc_or_desc}
        LIMIT 5
        """

        # 쿼리 실행
        cur.execute(query)




        df = pd.DataFrame(cur.fetchall())

        
        df['현재가'] = df["현재가"].apply(lambda x : format(x, ','))
        df['거래량'] = df["거래량"].apply(lambda x : format(x, ','))

        df['시가총액'] = df['시가총액'].apply(lambda x : self.format_number_to_unit(x))

        df['거래대금'] = df["거래대금"].apply(lambda x : self.format_number_to_unit(x))
        
        cur.close()

        return df
    
# a = StockForDB()
# print(a.get_top("KOSPI"))
