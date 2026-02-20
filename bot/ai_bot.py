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
            model=config("GROQ_MODEL", default="llama3-70b-8192"),
            temperature=float(config("TEMPERATURE", default="0.3")),
            max_tokens=int(config("MAX_TOKENS", default="2048")),
        )

        self.__chroma_dir = config("CHROMA_DIR", default="/app/chroma_data")
        self.__collection = config("CHROMA_COLLECTION", default="uni7_pdfs")
        self.__top_k = int(config("TOP_K", default="5"))

        self.__embeddings = HuggingFaceEmbeddings(
            model_name=config("EMBED_MODEL", default="sentence-transformers/all-MiniLM-L6-v2")
        )

        self.__db = Chroma(
            collection_name=self.__collection,
            persist_directory=self.__chroma_dir,
            embedding_function=self.__embeddings,
        )

    def _retrieve_context(self, question: str) -> str:
        docs = self.__db.similarity_search(question, k=self.__top_k)
        if not docs:
            return ""

        blocks = []
        for d in docs:
            meta = d.metadata or {}
            src = meta.get("source", "pdf")
            page = meta.get("page", "?")
            blocks.append(f"[{src} p.{page}] {d.page_content}")

        return "\n\n".join(blocks)

    def invoke(self, question: str) -> str:
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
        return chain.invoke({"pergunta": question, "contexto": context})