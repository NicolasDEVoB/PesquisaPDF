from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class PDFProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        # chunk_size: tamanho de cada pedaço de texto
        # chunk_overlap: o quanto um pedaço "repete" do anterior (ajuda a não perder contexto)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def process_pdf(self, file_path: str):
        """Lê o PDF e retorna uma lista de pedaços de texto (chunks)."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        # 1. Carrega o PDF
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()

        # 2. Divide em pedaços menores
        chunks = self.text_splitter.split_documents(documents)
        
        print(f"✅ PDF processado: {len(chunks)} pedaços gerados.")
        return chunks