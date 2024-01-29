# 총 4개의 라이브러리를 사용해서 비교
import FinanceDataReader as fdr
from pykrx import stock
import pandas_datareader.data as pdr
import yfinance as yf

# 라이브러리를 통해 주가 정보를 가져오는 Class 모음(여러 라이브러리를 비교해보고 제일 성능이 좋은 라이브러리 1개를 선택해야 함)
class StockForLibrary:
    
    """
    1. 주식 종목 정보
    """

    # fdr을 이용해서 현재 시점의 시장별 상장 종목 리스트 가져오기
    def get_stock_list_fdr(self, stock_type= "all"):
        stock_list = fdr.StockListing("KRX")
        

        if stock_type != "all":
            stock_list = stock_list[stock_list['Market']==stock_type].reset_index(drop=True)

        return stock_list
    
    # fdr을 이용해서 상장 폐지 종목 리스트 
    def get_stock_delete_list_fdr(self, stock_type="all"):
        stock_list = fdr.StockListing('KRX-DELISTING')
        if stock_type != "all":
            stock_list = stock_list[stock_list['Market']==stock_type].reset_index(drop=True)


        return stock_list
    
    # pykrx를 이용해서 특정 시점의 종목 번호 가져오기
    # 날짜("yyyy-mm-dd")를 명시해주지 않으면 가장 최근 영업일의 시장별 종목리스트를 가져옴
    def get_stock_list_pykrx(self, target_date=False):
        
        if target_date != False:
            ticker_list = stock.get_market_ticker_list(target_date)
        else:
            ticker_list = stock.get_market_ticker_list()

            
        return ticker_list

    """
    2. 상장 종목의 주가 조회 
        stock_code : 조회할 종목 코드
    """

    # fdr을 이용해서 조회 시점에 따라 주가 정보 가져옴 
    # 거래량 보정 X 
    def get_price_fdr(self, stock_code, start_date=False, end_date=False, target_year=False):
        
        # 특정 연부터 현재 시점까지
        if target_year != False:
            df_fdr = fdr.DataReader(stock_code, target_year)

            return  df_fdr
        

        df_fdr = fdr.DataReader(stock_code, start=start_date, end=end_date)
        
        
        return df_fdr
    
    # pykrx를 통해 주가 정보 가져오기 (날짜 형식 : "yyyymmdd")
    # 수정주가가 디폴트로 조회됨(adjusted 옵션으로 수정주가 여부 설정가능)
    # 거래량 보정 X 
    # adjusted=False로 조회하면 1995-05-02부터 조회되고, 거래대금과 등락률 칼럼이 추가됨
    def get_price_pykrx(self, stock_code, start_date="", end_date="", adjusted_stock=False):
        df_pykrx = stock.get_market_ohlcv_by_date(fromdate=start_date, 
                                          todate=end_date,
                                          ticker=stock_code,
                                          adjusted=adjusted_stock)
        
        return df_pykrx

    # pandas_datareader로 주가정보 가져오기 (날짜 형식 : "yyyy-mm-dd")
    # 데이터소스를 naver로 지정하면 1990년 데이터부터 조회할 수 있고, yahoo로 지정하면 2000년 데이터부터 조회할 수 있음
    # yahoo finance를 데이터소스로 사용할 때는 종목코드 뒤에 코스피 종목인 경우 .KS, 코스닥 종목인 경우 .KQ를 붙여줘야 함
    # yahoop의 경우 수정 주가 반영 
    def get_price_pdr(self, stock_code, start_date="", end_date="", data_source='naver'):
    
        df_pdr = pdr.DataReader(stock_code, data_source, start=start_date, end=end_date)


        return df_pdr

    # 야후 파이넨스를 이용해서 주가 정보 가져오기 (날짜 형식 : "yyyy-mm-dd")
    # end에 설정한 일자의 전일자까지 조회되기 때문에 조회하고자 하는 종료일+1일을 end에 넣어줘야함
    # 코스피 종목에는 .KS, 코스닥 종목에는 .KQ를 붙여줘야 함
    # yahoo의 경우 거래량이 액면분할을 고려한 상태로 조회 
    def get_price_yf(self, stock_code, start_date="", end_date=""):
        ticker = yf.Ticker(stock_code)
 
        df_day = ticker.history(
                    interval='1d',
                    start=start_date,
                    end=end_date,
                    actions=True,
                    auto_adjust=True)
        
        return df_day
    
    """
    Issue 1(2023.12.10)
    현재 yahoo에 있는 데이터를 가져오는 라이브러리에서 데이터를 불러올 때 오류가 발생하는 현상 발견
    추후에 해결이 필요해보임(아래 링크 참고)
    https://stackoverflow.com/questions/74832296/typeerror-string-indices-must-be-integers-when-getting-data-of-a-stock-from-y
    https://github.com/ranaroussi/yfinance/issues/1268

    """

# a = GetStockForLibrary() 
# print(a.get_price_fdr("005930", "2023-01-01", "2023-11-02"))
# print(a.get_price_pykrx("005930", "2023-01-01", "2023-11-02"))
