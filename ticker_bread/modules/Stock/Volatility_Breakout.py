from StockForLibrary import StockForLibrary
from pykrx import stock as pykrx_stock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

stock = StockForLibrary()

class VBS:
    def __init__(self):
        now = datetime.now()
        business_day_dt = datetime.strptime(pykrx_stock.get_nearest_business_day_in_a_week(), "%Y%m%d")
        self.end_date = business_day_dt.strftime("%Y%m%d")
        self.start_date = (datetime.strptime(self.end_date, "%Y%m%d") + timedelta(days=-1)).strftime("%Y%m%d")

    def VBS_today(self, stock_code, k):
        df = stock.get_price_pykrx(stock_code=stock_code, 
                                start_date=self.start_date, 
                                end_date=self.end_date, 
                                adjusted_stock=False)
        df['고가_전일자'] = df['고가'].shift(1)
        df['저가_전일자'] = df['저가'].shift(1)
        df['변동폭'] = df['고가_전일자'] - df['저가_전일자']
        df['목표가'] = (df['변동폭'] * k) + df['시가']
        df['매수'] = np.where(df['고가'] <= df['목표가'], 1, 0)
        return df['매수'].iloc[-1]
    
    def VBS_list(self, stock_code_list, k):
        

vbs_instance = VBS()
print(vbs_instance.VBS_today(stock_code="005930", k = 0.5))

