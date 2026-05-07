import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# ============================================================
# SINGLETON: a conexão com o Ollama é criada UMA ÚNICA VEZ.
# Evita reconectar ao modelo LLM a cada pergunta do usuário.
# ============================================================

# Pega a URL do Ollama da variável de ambiente 
# (padrão é localhost para rodar fora do Docker)
url_ollama = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

_modelo_llm = OllamaLLM(
    model="llama3.2:1b",
    base_url=url_ollama
)

# Template do prompt — também criado uma vez só
_template_prompt = """
### Instrução:
Você é um assistente acadêmico. Responda a PERGUNTA usando apenas o CONTEXTO fornecido.
Use Markdown (negrito e listas) e responda APENAS em Português.
Não repita estas instruções na resposta.

### Contexto:
{context}

### Pergunta:
{question}

### Resposta em Português:
"""

_prompt = PromptTemplate.from_template(_template_prompt)


class AIEngine:
    def __init__(self):
        # Reutiliza o modelo e o prompt já criados (singletons)
        self.model = _modelo_llm
        self.prompt = _prompt

    def generate_answer(self, question, context_docs):
        """Gera uma resposta usando o LLM com base nos trechos encontrados."""
        # Junta todos os trechos em um único texto de contexto
        texto_contexto = "\n\n".join([doc.page_content for doc in context_docs])

        # Monta a cadeia: prompt → modelo
        cadeia = self.prompt | self.model

        # Invoca o modelo com o contexto e a pergunta
        resposta = cadeia.invoke({
            "context": texto_contexto,
            "question": question
        })
        return resposta
