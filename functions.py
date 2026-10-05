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

    for cnpj in df_dados['CNPJ']:
        if pd.isna(cnpj):
            continue

        funil = df_dados.loc[df_dados['CNPJ'] == cnpj, 'Funil'].item()
        segmento = df_dados.loc[df_dados['CNPJ'] == cnpj, 'Segmento'].item()

        if pd.isna(funil) and not pd.isna(segmento):
            df_dados.loc[df_dados['CNPJ'] == cnpj, 'Funil'] = segmento


    df_dados = df_dados.drop(columns=['Segmento'])

    return df_dados


def update_somaoffice(df_somaoffice_atual : pd.DataFrame, df_somaoffice_passado : pd.DataFrame, df_unidades_municipios : pd.DataFrame):
    class DadosExluidos(Exception):
        pass

    try:

        df_verificacao_exclusao = pd.merge(df_somaoffice_passado, df_somaoffice_atual, how='left', on='CNPJ', indicator=True)

        df_verificacao_exclusao = df_verificacao_exclusao[df_verificacao_exclusao['_merge'] == 'left_only']

        if len(df_verificacao_exclusao) > 0:

            raise DadosExluidos('Dados Foram Exluídos! Verificar dados_excluidos.xlsx')

        df_somaoffice_merge_inner = pd.merge(df_somaoffice_passado, df_somaoffice_atual, how='inner', on='CNPJ')

        for cnpj in df_somaoffice_merge_inner['CNPJ']:

            if pd.isna(cnpj):
                continue

            funil_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Funil_x'].item()
            funil_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Funil_y'].item()

            grupo_empresarial_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'grupo_empresarial_x'].item()
            grupo_empresarial_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'grupo_empresarial_y'].item()

            nome_empresa_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'nome_empresa_x'].item()
            nome_empresa_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'nome_empresa_y'].item()

            municipio_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Município_x'].item()
            municipio_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Município_y'].item()

            nome_representante_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Nome Representante_x'].item()
            nome_representante_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Nome Representante_y'].item()

            uf_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'UF_x'].item()
            uf_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'UF_y'].item()
            
            cliente_fortes_passado = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Cliente Fortes?_x'].item()
            cliente_fortes_atual = df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Cliente Fortes?_y'].item()


            if (funil_passado != funil_atual) and not pd.isna(funil_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Funil_x'] = funil_atual

            if (grupo_empresarial_passado != grupo_empresarial_atual) and not pd.isna(grupo_empresarial_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'grupo_empresarial_x'] = grupo_empresarial_atual

            if (nome_empresa_passado != nome_empresa_atual) and not pd.isna(nome_empresa_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'nome_empresa_x'] = nome_empresa_atual   

            if (municipio_passado != municipio_atual) and not pd.isna(municipio_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Município_x'] = municipio_atual

            if (nome_representante_passado != nome_representante_atual) and not pd.isna(nome_representante_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Nome Representante_x'] = nome_representante_atual   

            if (uf_passado != uf_atual) and not pd.isna(uf_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'UF_x'] = uf_atual

            if (cliente_fortes_passado != cliente_fortes_atual) and not pd.isna(cliente_fortes_atual):
                df_somaoffice_merge_inner.loc[df_somaoffice_merge_inner['CNPJ'] == cnpj, 'Cliente Fortes?_x'] = cliente_fortes_atual 


        colunas_para_ficar = []

        for column in df_somaoffice_merge_inner.columns:
            if "_x" in column:
                colunas_para_ficar.append(column[:-2])

                df_somaoffice_merge_inner = df_somaoffice_merge_inner.rename(columns={column:column[:-2]})

        colunas_para_ficar.append('CNPJ')

        df_somaoffice_merge_inner = df_somaoffice_merge_inner[colunas_para_ficar]

        print(df_somaoffice_merge_inner.columns)

        print(df_somaoffice_merge_inner.count())



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

        print(df_somaoffice_merge_left.columns)

        print(df_somaoffice_merge_left.count())


        df_somaoffice_atualizado = pd.concat([df_somaoffice_merge_inner, df_somaoffice_merge_left], ignore_index=True)

        df_unidades_municipios = df_unidades_municipios.rename(columns={'CIDADE':'Município'})
        df_unidades_municipios['UNIDADE'] = df_unidades_municipios['UNIDADE'].str.upper()
        

        df_somaoffice_atualizado = pd.merge(df_somaoffice_atualizado, df_unidades_municipios, how='left', on=['Município', 'UF'])

        for cnpj in df_somaoffice_atualizado['CNPJ']:
            if pd.isna(cnpj):
                continue

            unidade = df_somaoffice_atualizado.loc[df_somaoffice_atualizado['CNPJ'] == cnpj, 'UNIDADE'].item()
            nome_representante = df_somaoffice_atualizado.loc[df_somaoffice_atualizado['CNPJ'] == cnpj, 'Nome Representante'].item()

            if pd.isna(nome_representante) and not pd.isna(unidade):
                df_somaoffice_atualizado.loc[df_somaoffice_atualizado['CNPJ'] == cnpj, 'Nome Representante'] = unidade

        df_somaoffice_atualizado = df_somaoffice_atualizado.drop(columns=['UNIDADE'])    

        return df_somaoffice_atualizado

    except DadosExluidos as e:
        print(f"Erro Detectado: {e}")

        return df_verificacao_exclusao
    
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
        df_somaoffice_totais = df_somaoffice_totais.iloc[:-3, 1:]

        today = date.today()

        ano = today.year

        dia_um = datetime(year=ano, month=1, day=1)

        meses = {"janeiro":1, "fevereiro":2, "março":3, "abril":4, "maio":5, "junho":6,
                "julho":7, "agosto":8, "setembro":9, "outubro":10, "novembro":11, "dezembro":12}

        meses_num = df_somaoffice_totais['Date - Mês'].str.strip().str.lower().map(meses)

        df_somaoffice_totais['Data'] = pd.to_datetime(
            pd.DataFrame({"year":ano, "month":meses_num, "day":1})
        )

        df_somaoffice_totais = df_somaoffice_totais.drop(columns=['Date - Mês'])

        ano_existe = (df_tempo_totais["Data"].dt.year == ano).any()

        if ano_existe:
            df_tempo_totais = df_tempo_totais.loc[df_tempo_totais['Data'] < dia_um]

        df_tempo_totais = pd.concat([df_tempo_totais, df_somaoffice_totais])

        return df_tempo_totais

    except Exception as e:
        raise e
            
    