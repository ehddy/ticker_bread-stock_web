import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr
import yfinance as yf
import psycopg2
import yaml
import requests as rq
from bs4 import BeautifulSoup as bs

class Indicators:
    def __init__(self, symbol):
        self.symbol = symbol
        self.recent_date = self.get_recent_date()
        self.data = self.get_data()

    # 최근 날짜 가져오기
    def get_recent_date(self):
        url = 'https://finance.naver.com/sise/'
        res = rq.get(url)
        html = bs(res.content, 'html.parser')
        recent_date = html.select_one('#time3').text.strip().split('장')[0].replace('.', '')
        recent_date = recent_date[:4] + '/' + recent_date[4:6] + '/' + recent_date[6:8]
        return recent_date

    # 지정된 종목의 데이터 가져오기
    def get_data(self):
        try:
            df = fdr.DataReader(self.symbol, end=self.recent_date)
        except:
            df = yf.download(self.symbol, end=self.recent_date)
        df['ChangeAmount'] = df['Close'].diff()
        df['Change'] = df['Close'].pct_change(fill_method=None)
        return df

    # 1. 최근 장 마감일 기준 값, 증감률, 증감액 가져오기
    def get_recent_data(self):
        recent_data = self.data.iloc[-1][['Close', 'Change', 'ChangeAmount']].to_frame().T
        recent_data['Change'] = recent_data['Change'].apply(lambda x: str(round(x * 100, 2)) + '%')
        recent_data['ChangeAmount'] = recent_data['ChangeAmount'].apply(lambda x: str(round(x*-1, 2)) if str(x)[0] == '-' else str(round(x, 2)))
        return recent_data

    # 2. 시계열 데이터프레임 리턴 (시작 날짜, 빈도 지정) - 장기적 추세 / 다양한 시간 단위 분석
    def get_index_data_over_time(self, start_date, freq='D'): # 'D'(일별), 'W'(주별), 'M'(월별), 'Y'(연별) 
        df = fdr.DataReader(self.symbol, start_date, self.recent_date)
        df = df.asfreq(freq, method='pad')
        return df[['Close']]
    
    # 3. 최근 30일간의 데이터 가져오기 - 단기 추세 분석 / 최근 주가 변동 확인
    def get_last_30_days_data(self):
        start_date = (datetime.strptime(self.recent_date, "%Y/%m/%d") - timedelta(days=30)).strftime("%Y-%m-%d")
        last_30_days_data = self.data.loc[start_date:self.recent_date]['Close']
        return last_30_days_data

    # 4. 코스피, 코스닥 상승 종목 수, 하락 종목 수 호출
    def get_up_down_count(self, index):
        # 전체 종목 리스트 가져오기
        total_list = fdr.StockListing('KRX')

        # 코스피, 코스닥 종목 코드 리스트 가져오기
        if index.lower() == 'kospi':
            index_list = total_list[total_list['Market'] == 'KOSPI']['Code'].tolist()
        elif index.lower() == 'kosdaq':
            index_list = total_list[total_list['Market'] == 'KOSDAQ']['Code'].tolist()

        # 각 종목의 마지막 날 데이터 가져오기
        up_count = 0
        down_count = 0
        for Code in index_list:
            try:
                data = fdr.DataReader(Code, end=self.recent_date)
                if data.iloc[-1]['Change'] > 0:
                    up_count += 1
                elif data.iloc[-1]['Change'] < 0:
                    down_count += 1
            except:
                continue

        result = pd.DataFrame({
            '상승 종목 수': [up_count],
            '하락 종목 수': [down_count]
        })

        return result


# 거래소별 종목코드 : StockListing()
# 한국거래소 : KRX(KOSPI, KOSDAQ, KONEX)
# 미국거래소 : NASDAQ, NYSE, AMEX, S&P500

# 가격데이터 - DataReader() 
# symbols : 
# 지수
# 코스피지수 : KS11
# 코스닥지수 : KQ11
# 다우지수 : DJI
# 나스닥지수 : IXIC
# S&P500 : US500

# 환율
# 달러/원 : USD/KRW
# 엔화/원 : JPY/KRW
# 위엔/원 : CNY/KRW
# 달러/유로 : USD/EUR
# 달러/엔화 : USD/JPY

# 금: GC=F (Comex 금)
# 원자재: ^CRB (CRB 원자재 지수)
# 유가: CL=F (WTI 원유)

# 암호화폐
# 비트코인 달러가격(비트파이넥스): BTC/USD 
# 비트코인 원화가격(빗썸): BTC/KRW

# Indicators = Indicators('JPY/KRW') 

# recent_data = Indicators.get_recent_data()
# df = Indicators.get_index_data_over_time('2020-01-01', 'D')
# last_30_days_data = Indicators.get_last_30_days_data()
# up_down_count = Indicators.get_up_down_count('kospi')

# kospi_listing = fdr.StockListing('KOSPI')
# 모든 열 이름 출력
# print(kospi_listing.columns)

# print(recent_data)
# print(last_30_days_data)
# print(up_down_count)