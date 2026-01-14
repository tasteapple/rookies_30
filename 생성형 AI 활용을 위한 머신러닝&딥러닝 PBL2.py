import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def print_data_info(df):
    print('------------- House Data Info ----------------')
    print(df.info(),"\n\n")
    print('------------- House Data Head ----------------')
    print(df.head(),"\n\n")

house_data = pd.read_csv('20260112_153749_train.csv') # 주택 가격 데이터셋 로드

print('------------- Before Preprocessing ----------------')
print_data_info(house_data)

# 결측치 확인 & 비율 출력
print('------------- Missing Values & Missing Ratio ----------------')
for i, j in enumerate(house_data.isnull().sum()):
    if j > 0:
        print(f'Column: {house_data.columns[i]}, Missing Values: {j}')
print()
missing_ratio = house_data.isna().mean().sort_values(ascending=False)
print(missing_ratio.head(20), '\n\n')

# 불필요한 열 제거 & 결측치 50% 이상인 열 제거
house_data = house_data.drop(columns=['Id'], axis=1)

threshold = 0.5  # 50% 이상이면 drop
drop_cols = missing_ratio[missing_ratio >= threshold].index.tolist()
drop_cols = [c for c in drop_cols]
house_data = house_data.drop(columns=drop_cols)


# 결측치 처리 (수치형: mean, 범주형: mode)
# 1) 수치형 컬럼 찾기 (int/float)
num_cols = house_data.select_dtypes(include=[np.number]).columns.tolist()

# 2) 범주형 컬럼 찾기 (object, category 등)
cat_cols = house_data.select_dtypes(exclude=[np.number]).columns.tolist()

# 3) 수치형 결측치 mean으로 채우기 (타겟 SalePrice는 건드리지 않게)
for col in num_cols:
    if col == 'SalePrice':
        continue
    if house_data[col].isna().any():
        house_data[col] = house_data[col].fillna(house_data[col].mean()) # LotFrontage 자동으로 처리됨

# 4) 범주형 결측치 mode로 채우기
for col in cat_cols:
    if house_data[col].isna().any():
        mode_val = house_data[col].mode(dropna=True)
        # mode가 비어있을 가능성까지 방어
        fill_val = mode_val.iloc[0] if len(mode_val) > 0 else "None"
        house_data[col] = house_data[col].fillna(fill_val)

# 5) 범주형 컬럼 get_dummies
house_data = pd.get_dummies(house_data, columns=cat_cols, drop_first=False)

print('------------- After Preprocessing ----------------')
print_data_info(house_data)

# 피처와 타겟 분리
X = house_data.drop(columns=['SalePrice'], axis=1)
y = house_data['SalePrice']

# 학습용/검증용 데이터 분리 8:2
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = DecisionTreeRegressor()
model.fit(X_train, y_train)

# 검증 데이터 예측
y_pred = model.predict(X_test)

# 성능 평가
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae}") 
print(f"MSE: {mse}")
print(f"RMSE: {rmse}")
print(f"R2 Score: {r2}")
