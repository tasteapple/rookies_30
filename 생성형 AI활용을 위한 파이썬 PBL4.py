import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class SalesAnalysis:
    def __init__(self, seed: int = 42):
        np.random.seed(seed) # 재현성을 위한 시드 고정
        # data_range를 사용하여 날짜 생성
        self.dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        # 1000에서 10,000 사이의 무작위 판매량 생성 - 일별 매출 데이터
        self.sales = np.random.randint(1000, 10001, size=len(self.dates))
        # DataFrame 생성
        self.df = pd.DataFrame({
            'Date' : self.dates,
            'Sales' : self.sales
        })
        print("Make DataFrame of 2024 Sales Data")
        print(self.df.head()) # 잘 생성되었는지 확인
        print("-" * 50)
    
    def calculte_monthly_sales(self):
        self.df['Month'] = self.df['Date'].dt.to_period('M') # Date 열에서 월 정보 추출
        self.monthly_sales = self.df.groupby('Month')['Sales'].sum().reset_index() # 월별 매출 합계 계산
        print("Monthly Sales Data")
        print(self.monthly_sales)
        print("-" * 50)
    
    def visualize_monthly_sales(self):
        plt.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "NanumGothic", "DejaVu Sans"] # OS 별 한글 폰트 설정
        plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

        x = self.monthly_sales['Month'].astype(str)  # 월을 문자열로 변환
        y = self.monthly_sales['Sales']
        
        plt.plot(x, y, marker='o', linestyle='-', color='b', label='월별 매출 합계')
        plt.title('2024년 월별 매출 합계')
        plt.xlabel('월')
        plt.ylabel('매출 합계 (원)')
        plt.xticks(ticks=range(1,13), labels=[f'{i}월' for i in range(1, 13)], rotation=45) # x축 레이블 회전 / 월 표시
        plt.grid(True, linestyle='--', alpha=0.7) # 그리드 추가
        plt.legend() # 범례 표시
        plt.tight_layout() # 레이아웃 조정
        plt.show()

if __name__ == "__main__":
    analysis = SalesAnalysis()
    analysis.calculte_monthly_sales()
    analysis.visualize_monthly_sales()
