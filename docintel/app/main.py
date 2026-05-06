from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path
import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
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


# Configuração de CORS (Essencial para seu futuro Frontend em React/JS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "DocIntel está online! Pronto para processar documentos."}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    file_path = UPLOAD_DIR / file.filename
    
    # Salva o upload de forma assíncrona
    async with aiofiles.open(file_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):  # 1MiB chunks
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
_executor = ThreadPoolExecutor(max_workers=4)

def process_and_index(path: str):
    """Processa PDF e salva embeddings usando thread pool para tarefas CPU‑bound."""
    loop = asyncio.get_event_loop()
    # Processamento do PDF (CPU‑bound)
    processor = PDFProcessor()
    chunks = loop.run_in_executor(_executor, processor.process_pdf, path)
    # Salvar vetores (CPU‑bound)
    v_manager = VectorStoreManager()
    # aguarda o resultado de chunks antes de salvar
    async def _save():
        resolved_chunks = await chunks
        await loop.run_in_executor(_executor, v_manager.save_chunks, resolved_chunks)
    asyncio.run(_save())
    # Opcional: remover o PDF temporário
    try:
        os.remove(path)
    except OSError:
        pass

if __name__ == "__main__":
    import uvicorn
    # Roda o servidor na porta 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
