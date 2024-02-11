import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from StockForDB import StockForDB
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

class VolumeIncrease:
    def __init__(self):
        self.stock = StockForDB() # DB에 연결
        self.engine = create_engine(f"postgresql://{self.stock.conn_info['user']}:{self.stock.conn_info['password']}@{self.stock.conn_info['host']}:{self.stock.conn_info['port']}/{self.stock.conn_info['database']}")

    def get_business_days(self):
        # 전일 기준 전일~20일간 평균 거래량 비교 -- 전일이 영업일이 아닐 수 있기 때문에 최근 영업일 기준으로 21일 영업일 날짜 불러오기
        query = """
        SELECT * FROM business_day
        WHERE business = 1
        ORDER BY date1 DESC
        LIMIT 21
        """
        business_days = pd.read_sql(query, self.engine)
        recent_business_day = business_days['date1'].iloc[0]
        start_date = business_days['date1'].iloc[-1]
        return recent_business_day, start_date

    def get_price_data(self, stock_code): 
        recent_business_day, start_date = self.get_business_days()
        recent_business_day = '-'.join([recent_business_day[:4], recent_business_day[4:6], recent_business_day[6:]]) # stock 테이블의 기준일자와 형식 맞추기
        start_date = '-'.join([start_date[:4], start_date[4:6], start_date[6:]])

        query = f"""
        SELECT * FROM stock
        WHERE 종목코드 = '{stock_code}' AND 기준일자 BETWEEN '{start_date}' AND '{recent_business_day}'
        """
        price_data = pd.read_sql(query, self.engine)
        return price_data

    def get_volume_surge(self, stock_code, ratio=10):
        price_data = self.get_price_data(stock_code)

        if price_data.empty: # 특정 종목코드에서 데이터 없는 경우 처리
            return None

        # 이전 20일 동안의 평균 거래량 계산 (최근 영업일 제외)
        avg_volume = price_data[:-1]['거래량'].mean()

        # 종목명 가져오기
        query = f"SELECT 종목명 FROM stock_info WHERE 종목코드 = '{stock_code}'"
        stock_name_df = pd.read_sql(query, self.engine)
        # 특정 종목코드에서 종목명 없는 경우 처리
        if stock_name_df.empty: 
            stock_name = None
        else:
            stock_name = stock_name_df['종목명'].iloc[0]

        # 최근 영업일의 거래량이 이전 20일 동안의 평균 거래량보다 ratio배 이상인지 확인
        if avg_volume != 0 and price_data.iloc[-1]['거래량'] / avg_volume >= ratio: 
            return {'종목코드': stock_code, '종목명': stock_name, '20일 평균 거래량': avg_volume, '급증 거래량': price_data.iloc[-1]['거래량']}
        else:
            return None

    def find_surged_stocks(self, ratio=10):
        # 모든 종목에 대하여 코드 수행
        query = "SELECT DISTINCT 종목코드 FROM stock"
        all_stocks = pd.read_sql(query, self.engine)
        surged_stocks = []

        # 작업 시간 오래 걸리기 때문에 병렬 처리하여 시간 단축시키기
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.get_volume_surge, stock_code, ratio) for stock_code in all_stocks['종목코드']]
            for future in concurrent.futures.as_completed(futures):
                surged_stock = future.result()
                # 거래량 급증 종목 리스트에 추가
                if surged_stock:
                    surged_stocks.append(surged_stock)

        # DataFrame 형태로 return
        return pd.DataFrame(surged_stocks)

# if __name__ == "__main__":
#     volume_increase = VolumeIncrease()
#     surged_stocks = volume_increase.find_surged_stocks(ratio=10) 
#     print(surged_stocks)