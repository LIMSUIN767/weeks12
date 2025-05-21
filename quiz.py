import pandas as pd
import numpy as np

df = pd.read_csv('서울대기오염_2019.csv', encoding='utf-8')  # 또는 encoding='cp949' 필요할 수 있음
print(df)