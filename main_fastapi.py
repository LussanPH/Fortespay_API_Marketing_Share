from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from functions import limpar_detalhamento_empresas, extrair_df_dados, update_somaoffice, update_somaoffice_tempo, update_somaoffice_tempo_totais
import pandas as pd
import numpy as np
import os
import io
import zipfile
from contextlib import asynccontextmanager
from pyngrok import ngrok
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["X-Erro", "Content-Disposition"],
)

ZIP = "application/zip"

# CSV no padrão do Excel pt-BR: separador ";", decimal "," e UTF-8 com BOM (senão os acentos quebram).
CSV_SEP = ";"
CSV_DECIMAL = ","


def ler_planilha(upload : UploadFile, sheet_name = 0, **kwargs):
    # Os arquivos gerados pela API voltam como .csv; os exports externos continuam .xlsx.
    if (upload.filename or "").lower().endswith(".csv"):
        return pd.read_csv(upload.file, sep=CSV_SEP, decimal=CSV_DECIMAL, encoding="utf-8-sig", low_memory=False, **kwargs)

    return pd.read_excel(upload.file, sheet_name=sheet_name, engine="calamine", **kwargs)


def decimal_em_colunas_mistas(df : pd.DataFrame):
    # O "decimal" do to_csv só vale para colunas float; em colunas object (ex.: histórico em texto "R$ 1.060" + linhas novas numéricas) o float sairia com ".".
    df = df.copy()

    for coluna in df.columns[df.dtypes == object]:
        df[coluna] = df[coluna].map(lambda v: str(v).replace(".", CSV_DECIMAL) if isinstance(v, float) and v == v else v)

    return df


def zip_csvs(abas : dict[str, pd.DataFrame]):
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for nome, df in abas.items():
            df = decimal_em_colunas_mistas(df)

            # to_csv sem caminho devolve str e ignora "encoding", por isso o encode.
            csv = df.to_csv(index=False, sep=CSV_SEP, decimal=CSV_DECIMAL)
            zf.writestr(f"{nome}.csv", csv.encode("utf-8-sig"))

    buffer.seek(0)

    return buffer


@app.post("/somaoffice_update")
async def somaoffice_update(detalhamento_empresas_somaoffice : UploadFile = File(...),
                            nectar_crm : UploadFile = File(...),
                            fortes_ag : UploadFile = File(...),
                            somaoffice_passado : UploadFile = File(...),
                            unidades_municipios : UploadFile = File(...)):
    
    try:
        df_somaoffice = ler_planilha(detalhamento_empresas_somaoffice, dtype={'CNPJ':str})
        df_base_crm = ler_planilha(nectar_crm, dtype={'CNPJ':str})
        df_base_ag = ler_planilha(fortes_ag, dtype={'CNPJ':str})
        df_somaoffice_passado = ler_planilha(somaoffice_passado, dtype={'CNPJ':str})
        df_unidades_municipios = ler_planilha(unidades_municipios, sheet_name='Unidades')

        df_somaoffice = limpar_detalhamento_empresas(df_somaoffice)

        df_dados = extrair_df_dados(df_somaoffice, df_base_ag, df_base_crm)

        df_somaoffice_passado, df_excluidos = update_somaoffice(df_dados, df_somaoffice_passado, df_unidades_municipios)

        houve_exclusao = len(df_excluidos) > 0

        abas = {"Somaoffice_passado": df_somaoffice_passado}

        if houve_exclusao:
            abas["Dados_Excluidos"] = df_excluidos

        buffer = zip_csvs(abas)

        headers = {"Content-Disposition":'attachment; filename="dadosatulizacao.zip"'}

        if houve_exclusao:
            headers["X-Erro"] = "Dados foram excluidos. Verificar Dados_Excluidos.csv em dadosatulizacao.zip"

        return StreamingResponse(
            buffer,
            status_code=409 if houve_exclusao else 200,
            media_type=ZIP,
            headers=headers
        )


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {e}")
    
    
@app.post('/somaoffice_tempo')
async def somaoffice_tempo(somaoffice_tempo : UploadFile = File(...),
                           somaoffice_tempo_total : UploadFile = File(...),
                           detalhamento_empresas : UploadFile =File(...),
                           somaoffice_totais : UploadFile = File(...)):

    try:
        df_somaoffice = ler_planilha(detalhamento_empresas, dtype={'cnpj':str})
        df_somaoffice_tempo = ler_planilha(somaoffice_tempo, sheet_name='Export', dtype={'cnpj':str})
        df_somaoffice_totais = ler_planilha(somaoffice_totais)
        df_tempo_totais = ler_planilha(somaoffice_tempo_total, sheet_name="Somaoffice_Tempo_Total", parse_dates=['Data'])
        
        df_somaoffice_limpo = limpar_detalhamento_empresas(df_somaoffice)
        
        
        df_somaoffice_tempo_grupos, df_somaoffice_tempo_empresas, df_somaoffice_tempo = update_somaoffice_tempo(df_somaoffice_limpo, df_somaoffice_tempo)

        df_tempo_totais = update_somaoffice_tempo_totais(df_somaoffice_totais, df_tempo_totais)
        
        buffer = zip_csvs({
            'Export': df_somaoffice_tempo,
            'Somaoffice_Tempo_Empresas': df_somaoffice_tempo_empresas,
            'Somaoffice_Tempo_Grupos': df_somaoffice_tempo_grupos,
            'Somaoffice_Tempo_Total': df_tempo_totais,
        })

        return StreamingResponse(
            buffer,
            media_type=ZIP,
            headers={"Content-Disposition":'attachment; filename="somaoffice_tempo.zip"'}
        )
        
        
    except Exception as e:
        logger.exception("Erro ao processar dados")
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {type(e).__name__}")
        
        


