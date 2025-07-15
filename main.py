from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import os

app = FastAPI()


@app.post("/process-kmz")
async def process_kmz(file: UploadFile = File(...)):
    # Verifica se é um arquivo .kmz
    if not file.filename.endswith(".kmz"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .kmz")

    # Aqui você processaria o arquivo real
    # Para fins de exemplo, simulamos a geração de um link de download
    # Em um caso real, você salvaria, processaria e geraria um .xlsx

    fake_xlsx_url = "https://kmz-api.onrender.com/files/resultado.xlsx"
    return JSONResponse(content={"downloadUrl": fake_xlsx_url})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return """
    <html>
        <head>
            <title>Política de Privacidade</title>
            <style>
                body { font-family: sans-serif; max-width: 700px; margin: auto; padding: 2em; line-height: 1.6; }
                h1 { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>Política de Privacidade</h1>
            <p>Este serviço processa arquivos KMZ para gerar planilhas XLSX com informações geográficas.</p>
            <p>Os arquivos são enviados temporariamente para nossos servidores e utilizados apenas para processamento técnico. Eles não são armazenados permanentemente, nem compartilhados com terceiros.</p>
            <p>Ao usar este assistente, você concorda com esse processamento temporário para fins exclusivamente técnicos.</p>
            <p>Recomendamos que você não envie dados sensíveis.</p>
        </body>
    </html>
    """

