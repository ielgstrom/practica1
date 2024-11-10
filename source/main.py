import pandas as pd
from utils import *

smi_data = get_smi_yearly_data()
print("a")
debt_data = get_debt_yearly_data()
print("b")
deficit_data = get_deficit_yearly_data()
#print(deficit_data)
#epa_data = get_epa_yearly_data() #complicat

df_joined = pd.merge(smi_data, debt_data, on=['Pais', 'Fecha'], how='outer')
df_joined = pd.merge(df_joined, deficit_data, on=['Pais', 'Fecha'], how='outer')
df_joined.head(n=10)
df_joined.to_csv('../dataset/dataset.csv', index=False)
