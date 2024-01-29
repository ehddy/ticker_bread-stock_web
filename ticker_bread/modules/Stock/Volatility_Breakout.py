# from StockForLibrary import StockForLibrary
# import FinanceDataReader as fdr
from pykrx import stock as pykrx_stock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class VBS:
    def __init__(self):
        now = datetime.now()
        business_day_dt = datetime.strptime(pykrx_stock.get_nearest_business_day_in_a_week(), "%Y%m%d")
        self.end_date = business_day_dt.strftime("%Y-%m-%d")
        self.start_date = (datetime.strptime(self.end_date, "%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d")

    def VBS(self, stock_code, k):
        ## fdr 라이브러리는 시가 정보 제공 X
        # df = fdr.DataReader(stock_code,
        #                     start = self.start_date,
        #                     end = self.end_date)
        df = pykrx_stock.get_market_ohlcv_by_date(ticker = stock_code,
                                                  fromdate = self.start_date, 
                                                  todate = self.end_date,
                                                  adjusted=False)
        df['고가_전일자'] = df['고가'].shift(1)
        df['저가_전일자'] = df['저가'].shift(1)
        df['변동폭'] = df['고가_전일자'] - df['저가_전일자']
        df['목표가'] = (df['변동폭'] * k) + df['시가']
        ## 매수 O = 1 & 매수 X = 0
        df['매수'] = np.where(df['고가'] <= df['목표가'], 1, 0)
        return df['매수'].iloc[-1]

vbs_instance = VBS()
# print(vbs_instance.VBS_today(stock_code="005930", k = 0.5))

