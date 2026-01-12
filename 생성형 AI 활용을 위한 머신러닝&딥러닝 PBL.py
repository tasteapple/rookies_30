import pandas as pd
from sklearn.preprocessing import MinMaxScaler
pd.set_option('future.no_silent_downcasting', True) # 경고문 제거용

df = pd.read_csv("diabetes.csv")

print('------- Info -------')
print(df.info(),'\n\n')
print('------- Head -------')
print(df.head(),'\n\n')
print('------- Before change 0 to NaN -------')
print(df.isnull().sum(),'\n\n')

# 결측치 처리
print('------- Missing Value Handling ------- \n')
# 0을 결측치로 간주 0 -> Nan
zero_to_nan = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI'] # 0을 결측치로 바꿀 컬럼명 리스트
df[zero_to_nan] = df[zero_to_nan].replace(0, pd.NA)

# 결측치 확인
print('------- Change 0 to NaN -------')
print(df.isnull().sum(),'\n\n')

# 결측치 -> 평균값 대체
for nan in zero_to_nan:
    df[nan] = df[nan].fillna(df[nan].mean())
print('------- After fill NaN with mean -------')
print(df.isnull().sum(),'\n\n')

# 이상치 처리
print('------- Outlier Handling -------')

# 이상치 컬럼명 리스트
over_data = ['SkinThickness', 'Insulin']

over_scores = {}
# 이상치(상위 1%) 갯수 확인
for over in over_data:
    over_score = df[over].quantile(0.99) # 상위 1% 기준값
    over_scores[over] = over_score

    over_mask = df[over] >= over_score
    print(f'{over} 이상치 갯수: {over_mask.sum()}')

# 이상치(상위 1%) -> 평균값 대체
for over in over_data:
    over_score = over_scores[over] # 상위 1% 기준값
    df.loc[df[over] >= over_score, over] = pd.NA # 이상치를 결측치로 변경 -- 이상치를 포함해서 평균을 내면 이상치의 영향이 남아있을 수 있기 때문
    df[over] = df[over].fillna(df[over].mean()) # 결측치(이상치) -> 평균값 대체

# 이상치 갯수 재확인
print('\n------- After Outlier Handling -------')
for over in over_data:
    over_score = over_scores[over] # 기존에 측정한 상위 1% 기준값
    over_mask = df[over] >= over_score
    print(f'{over} 이상치 갯수: {over_mask.sum()}')

# 정규화
print('\n------- Normalization -------')
scaler = MinMaxScaler()
df['Age'] = scaler.fit_transform(df[['Age']])
print('------- Finish Normalization -------\n\n')

# EDA
print('------- EDA -------\n')
print('------- Null Count After Preprocessing -------')
print(df.isnull().sum(),'\n\n')
# Outcome별 Glucose 평균
print('------- Outcome별 Glucose 평균 -------')
print(df.groupby('Outcome')['Glucose'].mean(),'\n\n')
# 데이터프레임 상위 5개 행 출력
print('------- DataFrame Head -------')
print(df.head(),'\n\n')