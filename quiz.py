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

# [8-1] pm10 값을 기준으로 등급 분류 (good/normal/bad/worse)
df_cleaned.loc[df_cleaned['pm10'] <= 30, 'pm10_grade'] = '좋음'
df_cleaned.loc[(df_cleaned['pm10'] > 30) & (df_cleaned['pm10'] <= 80), 'pm10_grade'] = '보통'
df_cleaned.loc[(df_cleaned['pm10'] > 80) & (df_cleaned['pm10'] <= 150), 'pm10_grade'] = '나쁨'
df_cleaned.loc[df_cleaned['pm10'] > 150, 'pm10_grade'] = '매우 나쁨'

# [8-2] 전체 데이터 기준 등급별 빈도, 비율 계산 (컬럼: pm_grade, n, pct)
pm10_grade_summary = df_cleaned['pm10_grade'].value_counts().reset_index()
pm10_grade_summary.columns = ['pm10_grade', 'count']
pm10_grade_summary['percentage'] = (pm10_grade_summary['count'] / pm10_grade_summary['count'].sum()) * 100
print('[8]')
print(pm10_grade_summary)

# [9-1] 구별 등급 분포 중 'good' 빈도와 전체 대비 비율 계산
total_by_district = df_cleaned.groupby('district').size()
good_by_district = df_cleaned[df_cleaned['pm10_grade'] == '좋음'].groupby('district').size()

good_ratio_df = (good_by_district / total_by_district).reset_index(name='pct')
good_ratio_df['n'] = good_by_district.values

# [9-2] 비율(pct) 기준 내림차순 정렬 후 상위 5개 구만 출력 (컬럼: district, n, pct)
top5_good_ratio = good_ratio_df.sort_values(by='pct', ascending=False).head(5)
print('[9]')
print(top5_good_ratio[['district', 'n', 'pct']])



import matplotlib.pyplot as plt
import seaborn as sns

# [10] 날짜별 PM10 평균 시각화
daily_pm10 = df_cleaned.groupby('date')['pm10'].mean().reset_index()

plt.figure(figsize=(14, 5))
sns.lineplot(data=daily_pm10, x='date', y='pm10', color='teal')
plt.title('Daily Trend of PM10 in Seoul, 2019')
plt.xlabel('Date')
plt.ylabel('PM10 (㎍/m³)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

#[11]
# 영어 등급명으로 바꿔서 결과 도출
df_cleaned['pm10_grade_eng'] = df_cleaned['pm10_grade'].map({
    '좋음': 'good',
    '보통': 'normal',
    '나쁨': 'bad',
    '매우 나쁨': 'worse'
})

#그룹화 진행
season_grade_dist = df_cleaned.groupby(['season', 'pm10_grade_eng']).size().reset_index(name='n')
season_grade_dist['pct'] = season_grade_dist['n'] / season_grade_dist.groupby('season')['n'].transform('sum') * 100

# 막대 그래프 시각화
plt.figure(figsize=(8, 6))
sns.barplot(
    data=season_grade_dist,
    x='season',
    y='pct',
    hue='pm10_grade_eng',
    hue_order=['good', 'normal', 'bad', 'worse']
)
plt.title('Seasonal Distribution of PM10 Grades in Seoul, 2019')
plt.ylabel('Percentage (%)')
plt.xlabel('Season')
plt.legend(title='PM10 Grade')
plt.tight_layout()
plt.show()