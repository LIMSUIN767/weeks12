import pandas as pd
import numpy as np

#[1-1] 데이터프레임으로 불러오기
df = pd.read_csv('201906.csv', encoding='utf-8')  # 또는 encoding='cp949' 필요할 수 있음

# [1-2] 분석변수만 추출 및 컬럼명 변경: date, district, pm10, pm25
df_subset = df[['날짜', '측정소명', '미세먼지', '초미세먼지']].copy()
df_subset.columns = ['date', 'district', 'pm10', 'pm25']

# [1-3] 결측치 확인 및 제거
missing_counts_original = df_subset.isnull().sum()
print(missing_counts_original) 
df_cleaned = df_subset.dropna() #결측치가 pm10 에서 213개, pm25에서 203개로 총 416개인데 전체 데이터 수가 9491개로 결측치는 다 제거해도 문제가 없을 것으로 판단
#missing_counts_cleaned = df_cleaned.isnull().sum()
#print(missing_counts_cleaned)

df_cleaned = df_cleaned[df_cleaned['district'] != '평균'] # 평균 값이라고 되어 있는 것들은 필요가 없으거라고 판단

# 이상치 확인
pm10_outliers = df_cleaned[(df_cleaned['pm10'] <= 0) | (df_cleaned['pm10'] >= 500)]
print("PM10 이상치 개수:", len(pm10_outliers))

pm25_outliers = df_cleaned[(df_cleaned['pm25'] <= 0) | (df_cleaned['pm25'] >= 300)]
print("PM2.5 이상치 개수:", len(pm25_outliers))
# 이상치 없으므로 넘어간다.


# [1-4] 자료형 변환: 문자형 → 날짜형, 실수형 등
# 날짜 컬럼: 문자열 → datetime
df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], errors='coerce')
df_cleaned = df_cleaned[df_cleaned['date'].notna()]

# 미세먼지 및 초미세먼지: 숫자형(float)
df_cleaned['pm10'] = df_cleaned['pm10'].astype(float)
df_cleaned['pm25'] = df_cleaned['pm25'].astype(float)


# [2-1] month, day 파생변수 생성
df_cleaned['month'] = df_cleaned['date'].dt.month
df_cleaned['day'] = df_cleaned['date'].dt.day


#[2-2] 계절(season) 변수 생성: month 기준으로 spring/summer/autumn/winter
df_cleaned.loc[df_cleaned['month'].isin([3, 4, 5]), 'season'] = 'spring'
df_cleaned.loc[df_cleaned['month'].isin([6, 7, 8]), 'season'] = 'summer'
df_cleaned.loc[df_cleaned['month'].isin([9, 10, 11]), 'season'] = 'autumn'
df_cleaned.loc[df_cleaned['month'].isin([12, 1, 2]), 'season'] = 'winter'

#[3-1] 최종 분석 대상 데이터 확인
print(df_cleaned.head())

#[3-2] csv로 output csv 저장
output_df = df_cleaned[['date', 'district', 'pm10', 'pm25', 'month', 'day', 'season']]
# CSV로 저장
output_df.to_csv('201906_output.csv', index=False, encoding='utf-8')


#[4-1] 전체 pm10 평균 구하기
avg_pm10 = df_cleaned['pm10'].mean()
print('[4]')
print(f'전체 pm10 평균: {avg_pm10:.2f}')

#[5-1] pm10 최댓값이 발생한 날짜, 구 출력'
print('[5]')
print(f"pm10 최댓값: {df_cleaned['pm10'].max()}") # 최댓값 구하기
pm10_max = df_cleaned[df_cleaned['pm10'] == df_cleaned['pm10'].max()] # 해당하는 행 구하기
print(f"pm10 최댓값이 발생한 날짜: {pm10_max.iloc[0]['date'].strftime('%Y-%m-%d')}")
print(f"pm10 최댓값이 발생한 구: {pm10_max.iloc[0]['district']}")

#[6-1] 각 구별 pm10 평균 계산
district_avg_pm10 = df_cleaned.groupby('district')['pm10'].mean().reset_index()
# 평균값 기준으로 내림차순 정렬
district_avg_pm10 = district_avg_pm10.sort_values(by='pm10', ascending=False)

# [6-2] 상위 5개 구만 출력 (컬럼: district, avg_pm10)
top5_district_pm10 = district_avg_pm10.head(5)
print('[6]')
print(top5_district_pm10)

# [7-1] 계절(season)별 평균 pm10, pm25 동시 계산
season_avg = df_cleaned.groupby('season')[['pm10', 'pm25']].mean().reset_index()

# [7-2] PM10 기준으로 오름차순 정렬
season_avg = season_avg.sort_values(by='pm10')
print('[7]')
print(season_avg)

