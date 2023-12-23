import pandas as pd
import yaml
import psycopg2
import psycopg2.extras as extras
from psycopg2.extras import RealDictCursor
import yaml 


class TodayNews:

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



    def get_top5_frequent_companied(self, stock_type='Kospi'):
        
        # 커서 생성
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        query = f"""
            SELECT * 
            FROM public."{stock_type}_News_frequent_Top5"
        """

        # 쿼리 실행
        cur.execute(query)

        df = pd.DataFrame(cur.fetchall())

        return df

