from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

class VectorStoreManager:
    def __init__(self, db_directory="data/db"):
        self.db_directory = db_directory
        # Este modelo transforma texto em 384 números (vetores)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def save_chunks(self, chunks):
        """Transforma chunks em vetores e salva no ChromaDB."""
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.db_directory
        )
        print(f"✅ {len(chunks)} vetores salvos no banco de dados em {self.db_directory}")
        return vector_db

    def get_relevant_documents(self, query, k=3):
        """Busca os 'k' pedaços de texto mais parecidos com a pergunta."""
        vector_db = Chroma(
            persist_directory=self.db_directory,
            embedding_function=self.embeddings
        )
        results = vector_db.similarity_search(query, k=k)
        return results