from pathlib import Path
from decouple import config

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


PDF_DIR = config("PDF_DIR", default="/app/data/pdfs")
CHROMA_DIR = config("CHROMA_DIR", default="/app/chroma_data")
COLLECTION = config("CHROMA_COLLECTION", default="uni7_pdfs")


def main():
    pdf_dir = Path(PDF_DIR)
    if not pdf_dir.exists():
        raise RuntimeError(f"PDF_DIR não existe: {pdf_dir}")

    docs = []
    for pdf_path in pdf_dir.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_path))
        docs.extend(loader.load())

    if not docs:
        raise RuntimeError(f"Nenhum PDF encontrado em {pdf_dir}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma(
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )
    db.add_documents(chunks)
    db.persist()

    print(f"✅ Indexado: páginas={len(docs)} | chunks={len(chunks)} | db={CHROMA_DIR} | collection={COLLECTION}")


if __name__ == "__main__":
    main()