import pandas as pd
import numpy as np

#[1-1] 데이터프레임으로 불러오기
df = pd.read_csv('201906.csv', encoding='utf-8')  # 또는 encoding='cp949' 필요할 수 있음

# [1-2] 분석변수만 추출 및 컬럼명 변경: date, district, pm10, pm25
df_subset = df[['날짜', '측정소명', '미세먼지', '초미세먼지']].copy()
df_subset.columns = ['date', 'district', 'pm10', 'pm25']

df_subset.head()

# [1-3] 결측치 확인 및 제거
missing_counts_original = df_subset.isnull().sum()
#print(missing_counts_original)
df_cleaned = df_subset.dropna()

#missing_counts_cleaned = df_cleaned.isnull().sum()
#print(missing_counts_cleaned)

# [1-4] 자료형 변환: 문자형 → 날짜형, 실수형 등
# 날짜 컬럼: 문자열 → datetime
df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], errors='coerce')

# 미세먼지 및 초미세먼지: 숫자형(float)
df_cleaned['pm10'] = df_cleaned['pm10'].astype(float)
df_cleaned['pm25'] = df_cleaned['pm25'].astype(float)

# 자료형 확인
df_cleaned.dtypes
df_cleaned
df_cleaned['date'].unique()
print(df_cleaned['date'].isna().sum()