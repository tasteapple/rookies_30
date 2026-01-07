import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class StudentScoreAnalysis:
    def __init__(self, seed :int = 42):
        np.random.seed(seed) # 재현을 위한 시드 고정
        
        students = [f'학생{i}' for i in range(1, 21)] # 학생 이름 생성 20명
        subjects = ['수학', '영어', '과학'] # 과목 리스트
        scores = np.random.randint(50, 101, size=(20, 3)) # 50~100점 사이의 랜덤 점수 생성 / 학생별 과목 점수 배열 생성
        self.__df = pd.DataFrame(scores, index=students, columns=subjects) # 데이터프레임 생성

        print("Make DataFrame of Student Scores")
        print(self.__df.head()) # 잘 생성되었는지 확인용 출력
        print("="*50)

        plt.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "NanumGothic", "DejaVu Sans"] # OS 별 한글 폰트 설정
        plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지
    
    def visualize_subject_average(self):
        subject_means = self.__df.mean(axis=0) # 과목별 평균 점수 계산 / 각 열의 평균
        x = subject_means.index # 과목 이름
        y = subject_means.values # 과목별 평균 점수 값
        bars = plt.bar(x, y, color=['skyblue', 'lightgreen', 'salmon']) # 막대 그래프 생성
        plt.title('과목별 평균 점수') # 그래프 제목
        plt.xlabel('과목') # x축 라벨
        plt.ylabel('평균 점수') # y축 라벨
        plt.ylim(0, 100) # y축 범위 설정 - 0~100
        plt.grid(axis='y') # y축에 그리드 추가

        # 막대 위에 점수 표시 (Text Annotation) - 디테일 점수 포인트
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, 
                     f'{height:.1f}점', ha='center', va='bottom')
        
        plt.show() # 그래프 출력
    
    def visualize_top5_students(self):
        self.__df['개인평균'] = self.__df.mean(axis=1) # 학생별 평균 점수 계산 / 각 행의 평균
        top5_students = self.__df.sort_values(by='개인평균', ascending=False).head(5) # 개인 평균 상위 5명 추출
        x = top5_students.index # 상위 5명 학생 이름
        y = top5_students['개인평균'].values # 상위 5명 학생 평균 점수 값

        bars = plt.bar(x, y, color='orange') # 막대 그래프 생성
        plt.title('개인 평균 상위 5명 학생') # 그래프 제목
        plt.xlabel('학생') # x축 라벨
        plt.ylabel('평균 점수') # y축 라벨
        plt.ylim(0, 100) # y축 범위 설정 - 0~100
        plt.grid(axis='y') # y축에 그리드 추가

        # 막대 위에 점수 표시 (Text Annotation) - 디테일 점수 포인트
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, 
                     f'{height:.1f}점', ha='center', va='bottom')
        
        plt.show() # 그래프 출력

if __name__ == "__main__":
    analysis = StudentScoreAnalysis() # 클래스 인스턴스 생성
    analysis.visualize_subject_average() # 과목별 평균 점수 시각화
    analysis.visualize_top5_students() # 개인 평균 상위 5명 학생 시각화