import requests
from io import BytesIO
import zipfile
import yaml

import xmltodict
import json
import pandas as pd

from datetime import date
from dateutil.relativedelta import relativedelta
from tabulate import tabulate

with open('../../config/config.yml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)


class GetDisclosure:

    def __init__(self):
        # api key 불러오기
        self.DART_KEY = _cfg['DART_KEY']

    # 종목 이름을 넣으면 기업 고유 번호와 종목 코드를 리턴
    def get_corp_code(self, corp_name):
        # 기업 고유 번호
        codezip_url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={self.DART_KEY}"

        codezip_data = requests.get(codezip_url)

        if codezip_data.status_code == 200:
            # 바이너리 스트림 형태로 변환 + 압축 풀기
            codezip_file = zipfile.ZipFile((BytesIO(codezip_data.content)))

            code_data = codezip_file.read('CORPCODE.xml').decode('utf-8')

            # 딕셔너리 형태로 변환
            data_odict = xmltodict.parse(code_data)

            data_dict = json.loads(json.dumps(data_odict))
            data = data_dict.get('result').get('list')
            corp_df = pd.DataFrame(data)

            # 상장된 주식만 가져오기
            corp_df = corp_df[~corp_df.stock_code.isin(
                [None])].reset_index(drop=True)
       
            # 종목 코드
            stock_code = corp_df.loc[corp_df['corp_name']
                                     == corp_name, 'stock_code'].values[0]

            # 고유 코드
            corp_code = corp_df.loc[corp_df['corp_name']
                                    == corp_name, 'corp_code'].values[0]

            return stock_code, corp_code

        else:
            print(f'연결 실패 {codezip_data.status_code}')
            return None

    # 기업의 이름과 조회 기간을 설정하면 해당 기업의 공시정보를 리턴
    def get_notice(self, corp_name, pre_date=30):
        try:
            stock_code, corp_code = self.get_corp_code(corp_name)
        except:
            print('주식 종목 이름을 정확하게 입력해주세요. ')
            return None

        # pre_date : 현재 날짜로부너 몇일 전인지 지정

        # 조회 시작 날짜 : default = 당일 1개월 전
        BGN_DE = (date.today() + relativedelta(days=-pre_date)
                  ).strftime('%Y%m%d')

        # 조회 종료 날짜 : default = 당일
        END_DE = (date.today()).strftime('%Y%m%d')

        # 법인 구분 (법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타)) 없으면 전체 조회
        CORP_CLS = ''

        # 페이지 번호 : default = 1
        PAGE_NO = '1'
        # 페이지당 건수(1~100) : default = 1, max = 100
        PAGE_COUNT = '100'

        # 공시 정보 데이터
        url = f'https://opendart.fss.or.kr/api/list.json?crtfc_key={self.DART_KEY}&corp_code={corp_code}&bgn_de={BGN_DE}&end_de={END_DE}&page_no={PAGE_NO}&page_count={PAGE_COUNT}'

        disclosure_data = requests.get(url)

        if disclosure_data.status_code == 200:
            # print('연결 성공')
            notice_data_df = disclosure_data.json().get('list')
            notice_data_df = pd.DataFrame(notice_data_df)

            # 공시 번호
            rcept_no = list(notice_data_df['rcept_no'])
    
            notice_data_df['url'] = notice_data_df['rcept_no'].apply(
                lambda x: f'https://dart.fss.or.kr/dsaf001/main.do?rcpNo={x}')

            notice_data_df = notice_data_df[['report_nm', 'rcept_dt', 'url']]

            notice_data_df = tabulate(
                notice_data_df, headers='keys', tablefmt='mysql')

            return notice_data_df

        else:
            return None

    def get_balance_sheet(self, corp_name, base_year="2022"):
        try:
            stock_code, corp_code = self.get_corp_code(corp_name)
        except:
            print('주식 종목 이름을 정확하게 입력해주세요. ')
            return None

        # 사업 연도(2015년부터 조회 가능)
        BSNS_YEAR = base_year

        ''' 1분기보고서 : 11013
        반기보고서 : 11012
        3분기보고서 : 11014
        사업보고서 : 11011
        '''
        REPRT_CODE = '11011'

        # CFS:연결재무제표, OFS:재무제표
        FS_DIV = 'OFS'

        balance_url = f'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key={self.DART_KEY}&corp_code={corp_code}&bsns_year={BSNS_YEAR}&reprt_code={REPRT_CODE}&fs_div={FS_DIV}'

        balance_data = requests.get(balance_url)

        if balance_data.status_code == 200:
            balance_data_df = balance_data.json().get('list')
            balance_data_df = pd.DataFrame(balance_data_df)

            balance_data_df = balance_data_df[['bsns_year', 'sj_nm', 'account_nm', 'thstrm_nm',
                                               'thstrm_amount', 'thstrm_add_amount', 'frmtrm_nm', 'frmtrm_amount']]

            return balance_data_df
        else:
            return None
# a = GetDisclosure()
# print(a.get_notice("삼성전자"))
# print(a.get_balance_sheet("삼성전자", base_year="2021"))