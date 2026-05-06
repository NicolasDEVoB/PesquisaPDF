from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

class AIEngine:
    def __init__(self, model_name: str = "llama3"):
        self.model = OllamaLLM(model=model_name)
        self.template = """
        Você é um assistente acadêmico para alunos de ADS. 
        Use APENAS os trechos abaixo para responder à pergunta do usuário.
        Se a resposta não estiver no texto, diga que não sabe.
        
        Contexto:
        {context}
        
        Pergunta:
        {question}
        
        Resposta curta e objetiva em Português:
        """
        self.prompt = PromptTemplate.from_template(self.template)

    def generate_answer(self, question, context_docs):
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        chain = self.prompt | self.model
        response = chain.invoke({
            "context": context_text,
            "question": question
        })
        return response
