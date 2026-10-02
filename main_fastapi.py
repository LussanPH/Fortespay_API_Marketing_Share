from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from functions import limpar_detalhamento_empresas, extrair_df_dados, update_somaoffice, update_somaoffice_tempo
import pandas as pd
import numpy as np
import os
import io
from contextlib import asynccontextmanager
from pyngrok import ngrok
from dotenv import load_dotenv


app = FastAPI()

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

@app.post("/somaoffice_update")
async def somaoffice_update(detalhamento_empresas_somaoffice : UploadFile = File(...),
                            nectar_crm : UploadFile = File(...),
                            fortes_ag : UploadFile = File(...),
                            somaoffice_passado : UploadFile = File(...),
                            unidades_municipios : UploadFile = File(...)):
    
    try:
        df_somaoffice = pd.read_excel(detalhamento_empresas_somaoffice.file, dtype={'CNPJ':str})
        df_base_crm = pd.read_excel(nectar_crm.file, dtype={'CNPJ':str})
        df_base_ag = pd.read_excel(fortes_ag.file, dtype={'CNPJ':str})
        df_somaoffice_passado = pd.read_excel(somaoffice_passado.file, dtype={'CNPJ':str})
        df_unidades_municipios = pd.read_excel(unidades_municipios.file, sheet_name='Unidades')

        df_somaoffice = limpar_detalhamento_empresas(df_somaoffice)

        df_dados = extrair_df_dados(df_somaoffice, df_base_ag, df_base_crm)

        df_somaoffice_passado = update_somaoffice(df_dados, df_somaoffice_passado, df_unidades_municipios)

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_somaoffice_passado.to_excel(writer, index=False, sheet_name="Somaoffice_passado")
            
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type=XLSX,
            headers={"Content-Disposition":'attachment; filename="dadosatulizacao.xlsx"'}
        )


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {e}")
    
    
@app.post('/somaoffice_tempo')
async def somaoffice_tempo(somaoffice_tempo : UploadFile = File(...),
                           detalhamento_empresas : UploadFile =File(...)):

    try:
        df_somaoffice = pd.read_excel(detalhamento_empresas.file, dtype={'cnpj':str})
        df_somaoffice_tempo = pd.read_excel(somaoffice_tempo.file, sheet_name='Export', dtype={'cnpj':str})
        
        df_somaoffice_limpo = limpar_detalhamento_empresas(df_somaoffice)
        
        
        df_somaoffice_tempo_grupos, df_somaoffice_tempo_empresas, df_somaoffice_tempo = update_somaoffice_tempo(df_somaoffice_limpo, df_somaoffice_tempo)
        
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_somaoffice_tempo.to_excel(writer, sheet_name='Export', index=False)
            
            df_somaoffice_tempo_empresas.to_excel(writer, sheet_name='Somaoffice_Tempo_Empresas', index=False)
            
            df_somaoffice_tempo_grupos.to_excel(writer, sheet_name='Somaoffice_Tempo_Grupos', index=False)
            
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type=XLSX,
            headers={"Content-Disposition":'attachment; filename="somaoffice_tempo.xlsx"'}
        )
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar dados: {e}")
        
        


