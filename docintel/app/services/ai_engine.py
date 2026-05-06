from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# ============================================================
# SINGLETON: a conexão com o Ollama é criada UMA ÚNICA VEZ.
# Evita reconectar ao modelo LLM a cada pergunta do usuário.
#
# ATENÇÃO sobre memória RAM:
#   - llama3     → precisa de ~4.6 GB (NÃO cabe em PCs com pouca RAM)
#   - tinyllama  → precisa de ~637 MB (leve, ideal para PCs modestos)
#   - llama3.2:1b → precisa de ~1.3 GB (boa qualidade, ainda leve)
#
# Troque o modelo abaixo conforme a RAM disponível no seu PC.
# ============================================================
_modelo_llm = OllamaLLM(model="tinyllama")

# Template do prompt — também criado uma vez só
# NOTA: as instruções de idioma são repetidas de propósito.
# Modelos pequenos (tinyllama) precisam de reforço para obedecer.
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
