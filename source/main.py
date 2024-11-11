from utils import *
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    future_smi = executor.submit(get_smi_yearly_data)
    future_debt = executor.submit(get_debt_yearly_data)
    future_deficit = executor.submit(get_deficit_yearly_data)

    smi_data = future_smi.result()
    debt_data = future_debt.result()
    deficit_data = future_deficit.result()

df_joined = pd.merge(smi_data, debt_data, on=['Pais', 'Fecha'], how='outer')
df_joined = pd.merge(df_joined, deficit_data, on=['Pais', 'Fecha'], how='outer')
df_joined.to_csv('../dataset/dataset.csv', index=False)
