from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
from pathlib import Path
import aiofiles
from .services.pdf_processor import PDFProcessor
from .services.vector_store import VectorStoreManager
from .services.ai_engine import AIEngine

app = FastAPI(
    title="DocIntel API",
    description="Sistema de busca semântica em documentos para estudantes de ADS",
    version="1.0.0"
)

# Caminho para salvar os uploads (usando a pasta que criamos na estrutura)
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Tamanho máximo de upload: 30 MB (protege contra arquivos enormes)
TAMANHO_MAXIMO_UPLOAD = 30 * 1024 * 1024  # 30 MB em bytes


# Configuração de CORS (Essencial para seu futuro Frontend em React/JS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de arquivos estáticos (Frontend)
# Vamos criar a pasta 'static' dentro de 'docintel/app'
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return {"message": "DocIntel está online! Acesse /pesquisa para o chat."}

@app.get("/pesquisa")
async def interface_pesquisa():
    # Retorna o arquivo HTML principal do nosso chat
    caminho_index = STATIC_DIR / "index.html"
    if not caminho_index.exists():
        return {"erro": "Arquivo index.html não encontrado na pasta static."}
    return FileResponse(str(caminho_index))

@app.get("/database")
async def interface_database():
    # Retorna o arquivo HTML da página do banco de dados
    caminho_db_html = STATIC_DIR / "database.html"
    if not caminho_db_html.exists():
        return {"erro": "Arquivo database.html não encontrado na pasta static."}
    return FileResponse(str(caminho_db_html))

@app.get("/api/database")
async def api_listar_documentos():
    # Retorna a lista de documentos em JSON
    v_manager = VectorStoreManager()
    documentos = v_manager.listar_documentos()
    return {"documentos": documentos}

@app.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    # Verifica se o arquivo é válido
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    # Verifica o tamanho do arquivo antes de processar
    tamanho_informado = request.headers.get("content-length")
    if tamanho_informado and int(tamanho_informado) > TAMANHO_MAXIMO_UPLOAD:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Máximo permitido: {TAMANHO_MAXIMO_UPLOAD // (1024*1024)}MB."
        )

    file_path = UPLOAD_DIR / file.filename
    
    # Salva o upload de forma assíncrona, controlando tamanho real
    tamanho_total = 0
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):  # 1MiB chunks
            tamanho_total += len(chunk)
            # Proteção extra: para se o arquivo real exceder o limite
            if tamanho_total > TAMANHO_MAXIMO_UPLOAD:
                await out.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"Arquivo muito grande. Máximo permitido: {TAMANHO_MAXIMO_UPLOAD // (1024*1024)}MB."
                )
            await out.write(chunk)

    # Envia o processamento pesado para o background
    background_tasks.add_task(process_and_index, str(file_path))
    return {"message": f"Arquivo {file.filename} recebido e será indexado."}

@app.get("/ask")
async def ask_question(question: str):
    v_manager = VectorStoreManager()
    ai = AIEngine()
    
    # 1. Busca os trechos relevantes no ChromaDB
    context_docs = v_manager.get_relevant_documents(question)
    
    if not context_docs:
        return {"answer": "Não encontrei informações sobre isso nos seus documentos."}
    
    # 2. IA gera a resposta baseada nesses trechos
    answer = ai.generate_answer(question, context_docs)
    
    # 3. Organiza as fontes para o usuário conferir
    sources = [
        {"documento": d.metadata.get("source"), "pagina": d.metadata.get("page")} 
        for d in context_docs
    ]
    
    return {
        "pergunta": question,
        "resposta": answer,
        "fontes": sources
    }

# Função de processamento em segundo plano
# (BackgroundTasks já roda isto numa thread separada, então é síncrono mesmo)
def process_and_index(caminho_pdf: str):
    """Processa o PDF e salva os embeddings no banco vetorial.
    
    Roda em background — não bloqueia a resposta HTTP.
    """
    # 1. Quebra o PDF em pedaços de texto
    processador = PDFProcessor()
    pedacos = processador.process_pdf(caminho_pdf)

    # 2. Transforma em vetores e salva no ChromaDB
    gerenciador_vetores = VectorStoreManager()
    gerenciador_vetores.save_chunks(pedacos)

    # 3. (Opcional) Remove o PDF temporário após indexar
    try:
        os.remove(caminho_pdf)
    except OSError:
        pass

@app.post("/limpar")
async def limpar_tudo():
    """Apaga todos os documentos enviados e limpa o banco de dados vetorial."""
    try:
        # 1. Limpa a pasta de uploads (caso tenha sobrado algo)
        if UPLOAD_DIR.exists():
            shutil.rmtree(UPLOAD_DIR)
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # 2. Limpa o banco de dados (pasta data/db)
        pasta_db = Path("data/db")
        if pasta_db.exists():
            shutil.rmtree(pasta_db)
            pasta_db.mkdir(parents=True, exist_ok=True)
            
        return {"message": "Tudo limpo! Você pode começar do zero agora."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar arquivos: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Roda o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
