from functions import update_somaoffice_tempo_totais
import pandas as pd

df_detalhamento_empresas = pd.read_excel('Detalhamento_Empresas.xlsx')

df_somaoffice_totais = pd.read_excel('Somaoffice_Tempo.xlsx', sheet_name='Somaoffice_Tempo_Total')

update_somaoffice_tempo_totais(df_detalhamento_empresas, df_somaoffice_totais)