import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class CustomerSalesAnalysis:
    def __init__(self, seed : int = 42):
        np.random.seed(seed) # 재현을 위한 시드 고정
        total_buy_count = 100

        customers = [f'Customer_{i}' for i in range(1, 11)] # 10명의 고객
        products = [f'Product_{i}' for i in range(1, 6)] # 5개의 제품

        data ={
            '고객' : [np.random.choice(customers) for _ in range(total_buy_count)], # 100개의 구매 기록 생성 - 고객 랜덤 선택
            '구매일자' : pd.date_range(start='2025-01-01', end='2025-12-31', periods=total_buy_count), # 100개의 구매 기록 생성 - 구매일자 랜덤 생성 / 시계열 날짜 생성
            '상품명' : [np.random.choice(products) for _ in range(total_buy_count)], # 100개의 구매 기록 생성 - 제품 랜덤 선택
            '수량' : np.random.randint(1, 11, size=total_buy_count), # 100개의 구매 기록 생성 - 1~10 사이의 랜덤 수량
            '단가' : np.random.randint(1000, 10001, size=total_buy_count) # 100개의 구매 기록 생성 - 1000~10000 사이의 랜덤 단가
        }

        self.df = pd.DataFrame(data)

        self.df['총매출'] = self.df['수량'] * self.df['단가'] # 총매출 컬럼 추가

        print(f"Make DataFrame with {total_buy_count} purchase records")
        print(self.df.head()) # 잘 생성되었는지 확인
        print("="*50)

        plt.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "NanumGothic", "DejaVu Sans"] # OS 별 한글 폰트 설정
        plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지
    
    def visualize_monthly_sales(self):
        self.df['월'] = self.df['구매일자'].dt.month # 구매일자에서 월 정보 추출
        monthly_sales = self.df.groupby('월')['총매출'].sum() # 월별 총매출 합계 계산
        x = monthly_sales.index # 월
        y = monthly_sales.values # 월별 총매출 값

        bars = plt.bar(x, y, color='skyblue') # 막대 그래프 생성
        plt.title('월별 총 구매 금액') # 그래프 제목
        plt.xlabel('월') # x축 라벨
        plt.ylabel('총 구매 금액') # y축 라벨
        plt.xticks(range(1,13), [f'{i}월' for i in range(1,13)]) # x축 눈금 설정 - 1~12월
        plt.grid(axis='y', linestyle='--', alpha=0.7) # y축에 그리드 추가

        # 막대 위 금액 표시 (천 단위 콤마 포함)
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, 
                     f'{int(height):,}원', ha='center', va='bottom', fontsize=9)
            
        plt.show() # 그래프 출력
    
    def visualize_customer_contribution(self):
        customer_sales = self.df.groupby('고객')['총매출'].sum().sort_values(ascending=False) # 고객별 총매출 합계 계산 및 정렬
        x = customer_sales.index # 고객 이름
        y = customer_sales.values # 고객별 총매출 값

        # 파이 차트 옵션 설정
        # autopct: 비율 표시 (%.1f%% -> 소수점 첫째자리까지)
        # startangle: 시작 각도 (90도에서 시작하면 보기 좋음)
        # explode: 1등 조각 떼어내기 효과
        explode = [0.05 if i == customer_sales.argmax() else 0 for i in range(len(customer_sales))]

        plt.pie(customer_sales, labels=x, autopct='%.1f%%', 
                startangle=90, explode=explode, shadow=True, 
                colors=plt.cm.Pastel1.colors) # 파스텔 톤 색상 사용
        
        plt.title('고객별 매출 기여도 분석', fontweight='bold')
        plt.show()


if __name__ == "__main__":
    analysis = CustomerSalesAnalysis()
    analysis.visualize_monthly_sales() # 월별 총 구매 금액 시각화
    analysis.visualize_customer_contribution() # 고객별 매출 기여도 시각화
