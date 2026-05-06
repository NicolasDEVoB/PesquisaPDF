docintel/
├── app/
│   ├── __init__.py
│   ├── main.py              # Ponto de entrada (FastAPI)
│   ├── core/
│   │   └── config.py        # Variáveis de ambiente e chaves de API
│   ├── services/
│   │   ├── pdf_processor.py # Lógica para ler e "quebrar" o PDF
│   │   ├── vector_store.py  # Conexão com ChromaDB/FAISS
│   │   └── ai_engine.py     # Integração com LLM (LangChain/Ollama)
│   ├── api/
│   │   └── endpoints.py     # Rotas da API (upload, query)
│   └── models/              # Schemas de dados (Pydantic)
├── data/
│   ├── uploads/             # Onde os PDFs originais ficarão
│   └── db/                  # Persistência do Banco Vetorial
├── tests/                   # Testes unitários
├── .env                     # Chaves secretas (não vai para o GitHub)
├── .gitignore               # Ignorar venv/ e arquivos de sistema
├── docker-compose.yml       # Orquestração do projeto
├── Dockerfile               # Configuração da imagem Python
└── requirements.txt         # Dependências do projeto