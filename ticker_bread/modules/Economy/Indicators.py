import pandas as pd
import FinanceDataReader as fdr
import requests as rq
from bs4 import BeautifulSoup as bs

class Indicators:
    def __init__(self):
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

# stock_data = StockData()

# recent_kospi_df = stock_data.get_recent_index_data('KS11')
# recent_kosdaq_df = stock_data.get_recent_index_data('KQ11')
# print(recent_kospi_df)
# print(recent_kosdaq_df)

# kospi_time_series_df = stock_data.get_index_data_over_time('KS11', '2023-01-01', 'D')
# kosdaq_time_series_df = stock_data.get_index_data_over_time('KQ11', '2023-01-01', 'D')
# print(kospi_time_series_df)
# print(kosdaq_time_series_df)
