import os
from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


os.environ["GROQ_API_KEY"] = config("GROQ_API_KEY")


class AIBot:
    def __init__(self):
        self.__chat = ChatGroq(
            model=config("GROQ_MODEL", default="llama-3.1-8b-instant"),
            temperature=float(config("TEMPERATURE", default="0.3")),
            max_tokens=int(config("MAX_TOKENS", default="2048")),
        )

        self.__chroma_dir = config("CHROMA_DIR", default="/app/chroma_data")
        self.__collection = config("CHROMA_COLLECTION", default="uni7_pdfs")
        self.__top_k = int(config("TOP_K", default="5"))

        self.__embeddings = HuggingFaceEmbeddings(
            model_name=config("EMBED_MODEL", default="sentence-transformers/all-MiniLM-L6-v2"),
            model_kwargs={'device': 'cpu'}
        )

        self.__db = Chroma(
            collection_name=self.__collection,
            persist_directory=self.__chroma_dir,
            embedding_function=self.__embeddings,
        )

    def _retrieve_context(self, question: str) -> str:
        docs = self.__db.similarity_search(question, k=self.__top_k)
        print(f"[AIBOT] Buscando contexto para: '{question}'")
        print(f"[AIBOT] Documentos encontrados: {len(docs)}")
        
        if not docs:
            print(f"[AIBOT] ⚠️  Nenhum documento encontrado!")
            return ""

        blocks = []
        for i, d in enumerate(docs, 1):
            meta = d.metadata or {}
            src = meta.get("source", "pdf")
            page = meta.get("page", "?")
            content_preview = d.page_content[:50].replace('\n', ' ')
            print(f"[AIBOT]   {i}. {src} p.{page}: {content_preview}...")
            blocks.append(f"[{src} p.{page}] {d.page_content}")

        context = "\n\n".join(blocks)
        print(f"[AIBOT] Contexto total: {len(context)} caracteres")
        return context

    def invoke(self, question: str) -> str:
        print(f"\n[AIBOT] === Processando pergunta: '{question}' ===")
        context = self._retrieve_context(question)

        prompt = PromptTemplate(
            input_variables=["pergunta", "contexto"],
            template="""
Você é um coordenador da Uni7 e responde alunos usando SOMENTE o conteúdo dos PDFs fornecidos.
Se a resposta não estiver no contexto, diga que não encontrou no material e peça mais detalhes.
Responda em português brasileiro, de forma objetiva e em passos quando fizer sentido.

<contexto>
{contexto}
</contexto>

Pergunta do aluno:
{pergunta}
""".strip(),
        )

        chain = prompt | self.__chat | StrOutputParser()
        print(f"[AIBOT] Invocando LLM com Groq...")
        response = chain.invoke({"pergunta": question, "contexto": context})
        print(f"[AIBOT] Resposta gerada: {response[:100]}...")
        print(f"[AIBOT] === Fim do processamento ===\n")
        return response