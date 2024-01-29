import FinanceDataReader as fdr
from pykrx import stock as pykrx_stock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class Bollinger_band:
    # def __init__(self):
        # now = datetime.now()
        # business_day_dt = datetime.strptime(pykrx_stock.get_nearest_business_day_in_a_week(), "%Y%m%d")
        # self.end_date = business_day_dt.strftime("%Y-%m-%d")
        # self.start_date = (datetime.strptime(self.end_date, "%Y-%m-%d") + timedelta(days=-30)).strftime("%Y-%m-%d")
    
    def business_day(self, n_days):
        now = datetime.now()
        business_day_dt = datetime.strptime(pykrx_stock.get_nearest_business_day_in_a_week(), "%Y%m%d")
        end_date = business_day_dt
        start_date = end_date - timedelta(days=n_days*2)
        period = (end_date - start_date).days
        
        dates = [d.strftime('%Y-%m-%d') for d in pd.date_range(start_date, periods=period+1)]
        dates_new = [d.strftime('%Y%m%d') for d in pd.date_range(start_date, periods=period+1)]
        dt_df = pd.DataFrame({
            'date_1' : dates,       ## 'yyyy-MM-dd' 형식 
            'date_2' : dates_new    ## 'yyyyMMdd' 형식
        })
        
        # 각 일자별 영업일 여부 판단 (1=영업일, 0=비영업일)
        dt_df['bus_date'] = dt_df['date_2'].apply(lambda x: 1 if x == pykrx_stock.get_nearest_business_day_in_a_week(x) else 0)
        
        bus_dates = dt_df[dt_df['bus_date']==1].copy()
        # 일자 내림차순 정렬
        bus_dates.sort_values(by='date_1', ascending = False, inplace = True) 
        # 기준일수만큼 반환
        bus_dates = bus_dates.iloc[:n_days]
        bus_dates.reset_index(drop = True, inplace = True)

        # 원하는 일자 서식값으로 뽑아내기
        bus_dates = bus_dates['date_1'].to_list()

        return bus_dates

    def Bollinger_band(self, stock_code, n_days, k):
        ## n일 전의 n일 이동평균이 필요함... 2배로 계산
        bus_dates = self.business_day(n_days = n_days*2)
        start_date = bus_dates[-1]
        end_date = bus_dates[0]

        df = fdr.DataReader(stock_code,
                            start = start_date,
                            end = end_date)
        
        # 종가 기준으로 계산
        df['rolling_mean'] = df['Close'].rolling(window = n_days).mean()
        df['rolling_std'] = df['Close'].rolling(window = n_days).std()

        df['upper_band'] = df['rolling_mean'] + (df['rolling_std']*k)
        df['lower_band'] = df['rolling_mean'] - (df['rolling_std']*k)

        # 매수, 매도 구분하는 함수 정의
        def signal(row):
            if row['Close'] < row['lower_band']:
                return 'Buy'
            elif row['Close'] > row['upper_band']:
                return 'Sell'
            else:
                return '-'

        df['Signal'] = df.apply(signal, axis=1)
        df['Sell'] = np.where(df['Signal']=='Sell', 1, 0)

        recent_date = df.iloc[-1, :]

        # 최근일의 매수/매도 여부 반환
        result = recent_date['Signal']

        # 최근일의 매수 여부만 반환
        # result = recent_date['Sell']

        return result

bollinger_instance = Bollinger_band()

# print(bollinger_instance.Bollinger_band(stock_code = '373220', 
#                                         n_days = 20, 
#                                         k = 2))


