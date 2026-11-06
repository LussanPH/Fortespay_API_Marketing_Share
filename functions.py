import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta


def limpar_detalhamento_empresas(df_somaoffice_bruto : pd.DataFrame):

    df_somaoffice_bruto = df_somaoffice_bruto.iloc[:-3, :]


    df_somaoffice_bruto['CNPJ'] = df_somaoffice_bruto['cnpj'].shift(-1)


    df_somaoffice_bruto['grupo_empresarial'] = df_somaoffice_bruto['Grupo Empresarial']

    df_somaoffice_bruto = df_somaoffice_bruto.drop(columns=['Grupo Empresarial', 'cnpj'])


    df_somaoffice_limpo = df_somaoffice_bruto.iloc[:-1, :]


    return df_somaoffice_limpo


def extrair_df_dados(df_base_somapay : pd.DataFrame, df_base_ag : pd.DataFrame, df_base_crm : pd.DataFrame):
    df_base_somapay_sem_total_e_na = df_base_somapay[(df_base_somapay['nome_empresa'] != 'Total')]
    if 'nome_empresa_real' in df_base_somapay_sem_total_e_na.columns:
        df_base_somapay_sem_total_e_na = df_base_somapay_sem_total_e_na.drop(columns=['nome_empresa'])
        df_base_somapay_sem_total_e_na = df_base_somapay_sem_total_e_na.rename(columns={'nome_empresa_real' : 'nome_empresa'})


    df_base_crm_cnpj_corrigido = df_base_crm.rename(columns={'Contato: CNPJ':'CNPJ'})
    df_base_crm_cnpj_corrigido['CNPJ'] = df_base_crm_cnpj_corrigido['CNPJ'].str.strip('"')
    df_base_crm_cnpj_corrigido['Contato: Razão Social'] = df_base_crm_cnpj_corrigido['Contato: Razão Social'].fillna('Nenhum')
    df_base_crm_cnpj_corrigido = df_base_crm_cnpj_corrigido.drop_duplicates(subset=['CNPJ'])



    #SOMAPAY X AG
    df_ag_somapay = pd.merge(df_base_ag, df_base_somapay_sem_total_e_na, on='CNPJ', how="inner")

    df_ag_somapay = df_ag_somapay.drop_duplicates(subset=['CNPJ'])

    df_ag_somapay = df_ag_somapay[['CNPJ', 'Nome Representante', 'Município', 'UF', 'grupo_empresarial', 'nome_empresa', 'Segmento']]



    #ASSOCIAÇÃO ENTRE TODOS OS DADOS DISPONÍVEIS
    df_somapay_crm = pd.merge(df_base_somapay_sem_total_e_na, df_base_crm_cnpj_corrigido, how='inner', on='CNPJ')

    df_somapay_ag_crm = pd.merge(df_somapay_crm, df_ag_somapay, how='inner', on='CNPJ')

    df_somapay_ag_crm = df_somapay_ag_crm.iloc[:, ~df_somapay_ag_crm.columns.duplicated()]

    df_somapay_ag_crm = df_somapay_ag_crm.drop(columns=['Empresas', 'Contato: UF', 'Unidade', 'Contato: município', 'Contato: Razão Social', 
                                                                    'nome_empresa_x', 'Prim cashin', 'Faturamento', 'Emp. Cash-in', 'Fat. /Empresa', 
                                                                    'Contas Cad', 'C. Cash-in', 'Fat./conta', 'Novas contas', 'Volume Cash-in', 'Cliente SE', 'Vol SE', 
                                                                    'Inadimp.', 'Custos Onboard.', 'grupo_empresarial_x', 'Funil'])


    df_somapay_ag_crm = df_somapay_ag_crm.rename(columns={'nome_empresa_y':'nome_empresa', 'grupo_empresarial_y':'grupo_empresarial'})



    df_SOMENTE_somapay_E_crm =  pd.merge(df_somapay_crm, df_ag_somapay, how='left', on='CNPJ', indicator=True)

    df_SOMENTE_somapay_E_crm = df_SOMENTE_somapay_E_crm[df_SOMENTE_somapay_E_crm['_merge']=='left_only']

    df_SOMENTE_somapay_E_crm = df_SOMENTE_somapay_E_crm.drop(columns=['_merge'])

    df_SOMENTE_somapay_E_crm = df_SOMENTE_somapay_E_crm.iloc[:, ~df_SOMENTE_somapay_E_crm.columns.duplicated()]

    df_SOMENTE_somapay_E_crm = df_SOMENTE_somapay_E_crm.drop(columns=['nome_empresa_y', 'Prim cashin', 'Faturamento', 'Emp. Cash-in', 'Fat. /Empresa', 'Contas Cad', 
                                                                'C. Cash-in', 'Fat./conta', 'Novas contas', 'Volume Cash-in', 'Cliente SE', 'Vol SE', 'Inadimp.', 
                                                                'Custos Onboard.', 'grupo_empresarial_y', 'Empresas', 'Município', 'UF', 'Nome Representante', 'Segmento'])

    df_SOMENTE_somapay_E_crm = df_SOMENTE_somapay_E_crm.rename(columns={'grupo_empresarial_x':'grupo_empresarial', 'nome_empresa_x':'nome_empresa', 'Contato: UF':'UF', 'Contato: município':'Município', 
                                                                                    'Unidade':'Nome Representante', 'Contato: Razão Social':'razao_social'})



    df_SOMENTE_somapay_E_ag = pd.merge(df_ag_somapay, df_somapay_crm, how='left', on='CNPJ', indicator=True)

    df_SOMENTE_somapay_E_ag = df_SOMENTE_somapay_E_ag[df_SOMENTE_somapay_E_ag['_merge']=='left_only']

    df_SOMENTE_somapay_E_ag = df_SOMENTE_somapay_E_ag.drop(columns=['_merge'])

    df_SOMENTE_somapay_E_ag = df_SOMENTE_somapay_E_ag.iloc[:, ~df_SOMENTE_somapay_E_ag.columns.duplicated()]

    df_SOMENTE_somapay_E_ag = df_SOMENTE_somapay_E_ag[['grupo_empresarial_x', 'nome_empresa_x', 'CNPJ', 'Nome Representante', 'Município', 'UF', 'Segmento']]

    df_SOMENTE_somapay_E_ag = df_SOMENTE_somapay_E_ag.rename(columns={'grupo_empresarial_x':'grupo_empresarial', 'nome_empresa_x':'nome_empresa'})



    df_somapay_E_crm_OU_somapay_E_ag_OU_somapay_crm_ag = pd.concat([df_SOMENTE_somapay_E_crm, df_SOMENTE_somapay_E_ag, df_somapay_ag_crm], ignore_index=True)



    df_SOMENTE_somapay = df_base_somapay_sem_total_e_na[~df_base_somapay_sem_total_e_na['CNPJ'].isin(df_somapay_E_crm_OU_somapay_E_ag_OU_somapay_crm_ag['CNPJ'])]

    df_SOMENTE_somapay = df_SOMENTE_somapay.drop(columns=['Empresas'])


    df_dados = pd.concat([df_somapay_ag_crm,
                        df_SOMENTE_somapay_E_crm,
                        df_SOMENTE_somapay_E_ag,
                        df_SOMENTE_somapay], ignore_index=True)

    df_dados = df_dados.drop_duplicates(subset=['CNPJ'])


    df_dados = df_dados[['CNPJ', 'Funil', 'grupo_empresarial', 'nome_empresa', 'Município', 'Nome Representante', 'UF', 'Cliente Fortes?', 'Segmento']]

    # Sem Funil, usa o Segmento.
    sem_funil = df_dados['CNPJ'].notna() & df_dados['Funil'].isna() & df_dados['Segmento'].notna()
    df_dados.loc[sem_funil, 'Funil'] = df_dados.loc[sem_funil, 'Segmento']


    df_dados = df_dados.drop(columns=['Segmento'])

    return df_dados


def update_somaoffice(df_somaoffice_atual : pd.DataFrame, df_somaoffice_passado : pd.DataFrame, df_unidades_municipios : pd.DataFrame):
    try:

        df_excluidos = df_somaoffice_passado[~df_somaoffice_passado['CNPJ'].isin(df_somaoffice_atual['CNPJ'])]

        df_somaoffice_merge_inner = pd.merge(df_somaoffice_passado, df_somaoffice_atual, how='inner', on='CNPJ')

        # O dado atual sobrescreve o passado quando existe e é diferente.
        colunas_atualizaveis = ['Funil', 'grupo_empresarial', 'nome_empresa', 'Município', 'Nome Representante', 'UF', 'Cliente Fortes?']

        tem_cnpj = df_somaoffice_merge_inner['CNPJ'].notna()

        for coluna in colunas_atualizaveis:
            passado = df_somaoffice_merge_inner[f'{coluna}_x']
            atual = df_somaoffice_merge_inner[f'{coluna}_y']

            mudou = tem_cnpj & atual.notna() & (passado != atual)

            df_somaoffice_merge_inner.loc[mudou, f'{coluna}_x'] = atual[mudou]


        colunas_para_ficar = []

        for column in df_somaoffice_merge_inner.columns:
            if "_x" in column:
                colunas_para_ficar.append(column[:-2])

                df_somaoffice_merge_inner = df_somaoffice_merge_inner.rename(columns={column:column[:-2]})

        colunas_para_ficar.append('CNPJ')

        df_somaoffice_merge_inner = df_somaoffice_merge_inner[colunas_para_ficar]





        df_somaoffice_merge_left = pd.merge(df_somaoffice_atual, df_somaoffice_passado, how='left', on='CNPJ', indicator=True)

        df_somaoffice_merge_left = df_somaoffice_merge_left[df_somaoffice_merge_left['_merge'] == 'left_only']

        df_somaoffice_merge_left = df_somaoffice_merge_left.drop(columns=['_merge'])

        colunas_para_ficar = []

        for column in df_somaoffice_merge_left.columns:
            if "_x" in column:
                colunas_para_ficar.append(column[:-2])

                df_somaoffice_merge_left = df_somaoffice_merge_left.rename(columns={column:column[:-2]})

        colunas_para_ficar.append('CNPJ')

        df_somaoffice_merge_left = df_somaoffice_merge_left[colunas_para_ficar]




        df_somaoffice_atualizado = pd.concat([df_somaoffice_merge_inner, df_somaoffice_merge_left], ignore_index=True)

        df_unidades_municipios = df_unidades_municipios.rename(columns={'CIDADE':'Município'})
        df_unidades_municipios['UNIDADE'] = df_unidades_municipios['UNIDADE'].str.upper()
        

        df_somaoffice_atualizado = pd.merge(df_somaoffice_atualizado, df_unidades_municipios, how='left', on=['Município', 'UF'])

        # Sem representante, usa a unidade da cidade.
        sem_representante = (df_somaoffice_atualizado['CNPJ'].notna()
                             & df_somaoffice_atualizado['Nome Representante'].isna()
                             & df_somaoffice_atualizado['UNIDADE'].notna())

        df_somaoffice_atualizado.loc[sem_representante, 'Nome Representante'] = df_somaoffice_atualizado.loc[sem_representante, 'UNIDADE']

        df_somaoffice_atualizado = df_somaoffice_atualizado.drop(columns=['UNIDADE'])

        if len(df_excluidos) > 0:
            df_somaoffice_atualizado = pd.concat([df_somaoffice_atualizado, df_excluidos.reindex(columns=df_somaoffice_atualizado.columns)], ignore_index=True)

        return df_somaoffice_atualizado, df_excluidos

    except Exception as e:
        
        raise e
    
    
def update_somaoffice_tempo(somaoffice_limpo : pd.DataFrame, somaoffice_tempo : pd.DataFrame):
    try:
        somaoffice_limpo = somaoffice_limpo.loc[somaoffice_limpo['Prim cashin'].notna()]
        
        somaoffice_limpo = somaoffice_limpo.rename(columns={'Contas Cad':'Contas Cad.', 'CNPJ':'cnpj', 'grupo_empresarial':'Grupo'})

        today = date.today()

        somaoffice_limpo['Mês'] = today.month

        somaoffice_limpo['Ano'] = today.year

        somaoffice_mes_ano_atual = somaoffice_tempo.loc[(somaoffice_tempo['Mês'] == today.month) & (somaoffice_tempo['Ano'] == today.year)]

        if somaoffice_mes_ano_atual.notnull().any().any():
            
            somaoffice_tempo = somaoffice_tempo.loc[~((somaoffice_tempo['Mês'] == today.month) & (somaoffice_tempo['Ano'] == today.year))]
            
            
        somaoffice_tempo = pd.concat([somaoffice_tempo, somaoffice_limpo], ignore_index=True)
            
        somaoffice_tempo_empresas = somaoffice_tempo[(somaoffice_tempo['cnpj'] != 'Total') & (~pd.isna(somaoffice_tempo['cnpj']))]
        
        somaoffice_tempo_empresas = somaoffice_tempo_empresas.drop(columns=['Grupo', 'Empresas', 'Prim cashin', 'Emp. Cash-in', 'Fat. /Empresa', 'Fat./conta', 'Grupo Empresarial'])
        
        somaoffice_tempo_grupos = somaoffice_tempo[(somaoffice_tempo['nome_empresa'] == 'Total') & (somaoffice_tempo['cnpj'] == 'Total')]
        
        somaoffice_tempo_grupos = somaoffice_tempo_grupos.drop(columns=['nome_empresa', 'Empresas', 'Prim cashin', 'Fat. /Empresa', 'Fat./conta', 'Grupo Empresarial', 'cnpj'])
        
        return somaoffice_tempo_grupos, somaoffice_tempo_empresas, somaoffice_tempo
    
    except Exception as e:
        raise e
    
    
def update_somaoffice_tempo_totais(df_somaoffice_totais : pd.DataFrame, df_tempo_totais : pd.DataFrame):
    try:
        df_somaoffice_totais = df_somaoffice_totais.iloc[:-3, :]

        today = date.today()

        ano = today.year

        dia_um = datetime(year=ano, month=1, day=1)

        meses = {"janeiro":1, "fevereiro":2, "março":3, "abril":4, "maio":5, "junho":6,
                "julho":7, "agosto":8, "setembro":9, "outubro":10, "novembro":11, "dezembro":12}

        meses_num = df_somaoffice_totais['Date - Mês'].str.strip().str.lower().map(meses)

        df_somaoffice_totais['Data'] = pd.to_datetime(
            pd.DataFrame({"year":ano, "month":meses_num, "day":1})
        )
        
        df_somaoffice_totais['Data'] = df_somaoffice_totais['Data'].dt.date

        df_somaoffice_totais = df_somaoffice_totais.drop(columns=['Date - Mês'])

        # No CSV, "Data" pode misturar "2024-01-01 00:00:00" e "2026-01-01"; o parse_dates desiste e deixa a coluna como texto. ISO8601 aceita os dois formatos.
        df_tempo_totais["Data"] = pd.to_datetime(df_tempo_totais["Data"], format="ISO8601")

        ano_existe = (df_tempo_totais["Data"].dt.year == ano).any()

        if ano_existe:
            df_tempo_totais = df_tempo_totais.loc[df_tempo_totais['Data'] < dia_um]

        df_tempo_totais = pd.concat([df_tempo_totais, df_somaoffice_totais])

        # O histórico vem como datetime e as linhas novas como date; unifica para o CSV sair com um formato só.
        df_tempo_totais['Data'] = pd.to_datetime(df_tempo_totais['Data'])

        return df_tempo_totais

    except Exception as e:
        raise e
            
    