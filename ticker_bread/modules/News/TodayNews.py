import pandas as pd
import yaml
import psycopg2
import psycopg2.extras as extras
from psycopg2.extras import RealDictCursor
import yaml 
from konlpy.tag import Okt

import re

# 자연어 처리 패키지
import nltk

# 워드 클라우드 
from wordcloud import WordCloud

import matplotlib.pyplot as plt


plt.rc('font', family='AppleGothic')

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

        self.font_path = './BMHANNA_11yrs_ttf.ttf'

    def clean_text(self, x):
        # 구두점 제거 
        x = re.sub(r'[@%\\*=()/~#&\+á?\xc3\xa1\-\|\.\:\;\!\-\,\_\~\$\'\"]', '', x) 
        # 숫자 제거 
        x = re.sub(r'\d+','', x)
        # 소문자로 변환 
        x = x.lower()
        # 여백 제거 
        x = re.sub(r'\s+', ' ', x) 
        x = re.sub(r'<[^>]+>','',x) 
        x = re.sub(r'\s+', ' ', x)
        x = re.sub(r"^\s+", '', x) 
        x = re.sub(r'\s+$', '', x) 
        # 중국어 제거
        x = re.sub(r'[一-龥]', '', x) 
        
        # ㅋㅋ,ㅎㅎ, ㅠㅠ제거 
        x = re.sub(r'ㅋ|ㅎ|ㅠ', '', x) 
        
        # 특수문자 제거 
        x = re.sub('[-=+,#:;//●<>▲\?:^$.☆!★()Ⅰ@*\"※~>`\'…》]', ' ', x)
        

        return x

    def preprocessing_text(self, data):

        stop_word = pd.read_csv('./한국어불용어100.txt', sep = '\t', header = None, names = ['형태','품사','비율'])
        stop_words = list(stop_word['형태'])    
        
        # 한국어 자연어 처리 라이브러리 - 
        okt = Okt()

        token_list = []

        text = list(data['news_read_preprocessing'])

            # 워드 클라우드용 
        for i in range(len(text)):
            temp_X = []
            
            # 품사 태깅한다음 원하는 품사만 추출 
            temp_X = okt.pos(text[i])
            
            # 불용어 사전에 포함되어 있다면 해당 토큰 제거
            noun_adj_list = []
            
            for word, tag in temp_X:
                # 명사와 형용사만 추출 
                # 불용어 사전에 포함되어 있다면 해당 토큰 제거
                # 1글자 단어 제거
                if word not in stop_word and len(word) > 1 :
                    if tag == 'Noun':
                        noun_adj_list.append(word)
                    # elif tag == 'Verb' or tag == 'Adjective':
                    #     # 형용사일 경우 + 다 
                    #     noun_adj_list.append(word)

            token_list.append(noun_adj_list)
            
        data['token_for_wordcloud'] = token_list  

        remove_set = set(['시장','사업', '설명','기업','통해', '사용', '제품','이번', '같다', '없다', '되다','하다', '있다', '다음', '가능'])
    
        data['token_for_wordcloud'] = data['token_for_wordcloud'].apply(lambda x : [i for i in x if i not in remove_set])

        data['단어 개수'] = data['token_for_wordcloud'].apply(lambda x: len(x))


        data['corpus'] = data['token_for_wordcloud'].apply(lambda x: " ".join(x))


        return data

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

    # 워드 클라우드 생성
    def make_wordcloud(self, text, title):
        word_max = 1000
        wordcloud = WordCloud(font_path=self.font_path, background_color='white',\
                        max_words=word_max, max_font_size=200, height=700, width=900).generate(text)
        
        plt.figure(20) #이미지 사이즈 지정
        plt.imshow(wordcloud, interpolation='lanczos') #이미지의 부드럽기 정도
        plt.axis('off') #x y 축 숫자 제거

        plt.savefig(f'{title}_wordcloud.png')



    def get_wordcloud(self):
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT title, corp_name, news_read_preprocessing
            FROM today_finance_news
        """

        # 쿼리 실행
        cur.execute(query)

        df = pd.DataFrame(cur.fetchall())

        df = self.preprocessing_text(df)

        corpus = ''

        for i in range(len(df)):
            corpus += str(df['corpus'][i]) + ' '


        self.make_wordcloud(corpus, 'total')

        corpus = ''

        for i in range(len(df)):
            corpus += str(df['corp_name'][i]) + ' '
        
        print(corpus)

        self.make_wordcloud(corpus, 'corp_name')

a = TodayNews()

a.get_wordcloud()