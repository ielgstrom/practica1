from utils import *  # Importem tot el necessari per a fer la captura de dades de util.py.

smi_data = get_smi_yearly_data()  # Obtenim les dades relacionades amb l'SMI.
debt_data = get_debt_yearly_data()  # Obtenim les dades relacionades amb el deute.
deficit_data = get_deficit_yearly_data()  # Obtenim les dades relacionades amb el dèficit.
atur_data = get_atur_yearly_data()  # Obtenim les dades relacionades amb l'atur.
pib_data = get_pib_yearly_data()  # Obtenim les dades relacionades amb el PIB.
ipc_data = get_ipc_data()  # Obtenim les dades relacionades amb l'IPC.
codes_data = get_codes()  # Obtenim els codis dels països.
get_flags(codes_data)  # Obtenim les banderes a partir dels codis.

df_joined = pd.merge(smi_data, debt_data, on=['Pais', 'Fecha'], how='outer')  # Ajuntem els dataframes en un sol dataframe, segons el pais i l'any.
df_joined = pd.merge(df_joined, deficit_data, on=['Pais', 'Fecha'], how='outer')
df_joined = pd.merge(df_joined, atur_data, on=['Pais', 'Fecha'], how='outer')
df_joined = pd.merge(df_joined, pib_data, on=['Pais', 'Fecha'], how='outer')
df_joined = pd.merge(df_joined, ipc_data, on=['Pais', 'Fecha'], how='outer')
df_joined = pd.merge(df_joined, codes_data, on=['Pais'], how='outer')
df_joined.to_csv('../dataset/dataset.csv', index=False)  # Desem el resultat com a CSV.