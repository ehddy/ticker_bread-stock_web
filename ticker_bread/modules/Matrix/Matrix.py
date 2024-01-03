import pandas as pd

class Matrix:

    # 화폐의 미래 가치
    def future_value_of_money(self, current_money, interest_rate, duration_year):
        # 미래가치 = 현재금액 * (1 + 이자율) ^ 기간
        fv = current_money * (1 + interest_rate)**duration_year
        fv = int(fv)

        # 연(산술) 평균 수익 = (미래가치 - 현재금액) / 투자 기간
        avg_year_revenue =  int((fv - current_money) / duration_year)

        # 월 수익 = 연 평균 수익 / 12  
        avg_month_revenue = int(avg_year_revenue / 12)

        # 연 단리 수익률  = 연 평균 수익 / 현재금액  
        simple_interest =  round((avg_year_revenue / current_money) * 100, 1)

        result = [interest_rate, duration_year, current_money, fv, avg_year_revenue, avg_month_revenue, simple_interest]
        print(result)
        df = pd.DataFrame(data=[result], columns=['수익률', '기간', '투자금', '결과', '연(산술) 평균 수익', '월 수익', '단리 수익률'])
        
        
        return df 

    

