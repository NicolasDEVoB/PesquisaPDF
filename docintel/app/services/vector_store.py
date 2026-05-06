from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

# ============================================================
# SINGLETON: o modelo de embeddings é carregado UMA ÚNICA VEZ
# quando o módulo é importado. Isso evita recarregar ~90MB de
# modelo a cada requisição, economizando RAM e CPU.
# ============================================================
_modelo_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


class VectorStoreManager:
    def __init__(self, diretorio_banco="data/db"):
        # Reutiliza o modelo de embeddings já carregado (singleton)
        self.diretorio_banco = diretorio_banco
        self.embeddings = _modelo_embeddings

    def save_chunks(self, chunks):
        """Transforma chunks em vetores e salva no ChromaDB."""
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.diretorio_banco
        )
        print(f"✅ {len(chunks)} vetores salvos no banco de dados em {self.diretorio_banco}")
        return vector_db

    def get_relevant_documents(self, query, k=3):
        """Busca os 'k' pedaços de texto mais parecidos com a pergunta."""
        vector_db = Chroma(
            persist_directory=self.diretorio_banco,
            embedding_function=self.embeddings
        )
        resultados = vector_db.similarity_search(query, k=k)
        return resultados