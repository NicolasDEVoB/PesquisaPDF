# 🧠 DocIntel - Pesquisa Semântica em PDFs

O **DocIntel** é um assistente acadêmico inteligente projetado para ajudar estudantes a encontrarem informações em seus documentos PDF de forma rápida e precisa. Ao invés de uma busca comum por palavras-chave, o DocIntel entende o **contexto** da sua pergunta e busca a resposta diretamente nos seus documentos usando Inteligência Artificial.

---

## 🚀 Como funciona?

1.  **Upload**: Você envia um arquivo PDF.
2.  **Processamento**: O sistema lê o documento e o divide em pequenos pedaços (chunks).
3.  **Vetorização**: Cada pedaço é transformado em um vetor numérico (embedding) que representa o significado do texto.
4.  **Busca Semântica**: Quando você faz uma pergunta, o sistema busca os pedaços de texto mais parecidos com o sentido da sua dúvida.
5.  **Resposta com IA**: O modelo **Llama 3.2 (1b)** lê esses trechos e gera uma resposta clara e em português para você.

---

## 🛠️ Tecnologias Utilizadas

Segue a lista com as tecnologias utilizadas no projeto:

*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python) - Rápido, moderno e fácil de entender.
*   **Inteligência Artificial (LLM)**: [Ollama](https://ollama.com/) rodando o modelo **Llama 3.2:1b**.
*   **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace.
*   **Banco Vetorial**: [ChromaDB](https://www.trychroma.com/) - Para armazenar e buscar os significados dos textos.
*   **Orquestração de IA**: [LangChain](https://www.langchain.com/) - Para conectar os documentos ao modelo de linguagem.
*   **Frontend**: HTML5, CSS3 e JavaScript (Vanilla) - Interface limpa e responsiva sem frameworks pesados.

---

## 📦 Estrutura do Projeto

```text
docintel/
├── app/
│   ├── main.py              # Coração da API (Rotas e Inicialização)
│   ├── services/
│   │   ├── pdf_processor.py # Lógica para ler e dividir o PDF
│   │   ├── vector_store.py  # Gerenciamento do banco de dados de vetores
│   │   └── ai_engine.py     # Cérebro da IA (Integração com Ollama)
│   └── static/              # Interface Visual (HTML/CSS/JS)
├── data/
│   ├── db/                  # Onde o conhecimento é armazenado (ChromaDB)
│   └── uploads/             # Pasta temporária para arquivos enviados
└── requirements.txt         # Lista de ingredientes (dependências)
```

---

## ⚙️ Como Rodar o Projeto

### 1. Pré-requisitos
*   Python 3.10 ou superior.
*   [Ollama](https://ollama.com/) instalado e rodando.
*   Modelo Llama 3.2:1b baixado:
    ```bash
    ollama pull llama3.2:1b
    ```

### 2. Instalação
Clone o repositório e instale as dependências:
```bash
python -m venv .venv
source .venv/bin/activate  # No Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Execução Local (Sem Docker)
Inicie o servidor:
```bash
uvicorn docintel.app.main:app --reload
```
Acesse no seu navegador: `http://localhost:8000/pesquisa`

### 4. Execução com Docker (Recomendado)
Para rodar tudo (API + Ollama) de forma isolada:
```bash
docker-compose up --build
```
*Nota: Na primeira vez, você precisará baixar o modelo dentro do container:*
```bash
docker exec -it ollama_service ollama pull llama3.2:1b
```

---

## 📜 Filosofia de Desenvolvimento

Este projeto segue o princípio de código simples e legível.