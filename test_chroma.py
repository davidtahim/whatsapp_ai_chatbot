#!/usr/bin/env python
"""Script para testar o banco Chroma e a busca de documentos."""

import os
from pathlib import Path
from decouple import config

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def test_chroma():
    chroma_dir = config("CHROMA_DIR", default="/app/chroma_data")
    collection = config("CHROMA_COLLECTION", default="uni7_pdfs")
    
    print(f"📂 Diretório Chroma: {chroma_dir}")
    print(f"📦 Collection: {collection}")
    
    # Verificar se o diretório existe
    if not Path(chroma_dir).exists():
        print("❌ Diretório Chroma não existe!")
        return
    
    # Listar arquivos no diretório
    print(f"\n📋 Arquivos no diretório Chroma:")
    for item in Path(chroma_dir).iterdir():
        print(f"   - {item.name}")
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=config("EMBED_MODEL", default="sentence-transformers/all-MiniLM-L6-v2"),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        
        db = Chroma(
            collection_name=collection,
            persist_directory=chroma_dir,
            embedding_function=embeddings,
        )
        
        # Contar documentos
        docs_count = db._collection.count()
        print(f"\n✅ Banco Chroma carregado com sucesso!")
        print(f"📊 Total de documentos indexados: {docs_count}")
        
        if docs_count == 0:
            print("⚠️  Nenhum documento indexado! Execute: python ingest_pdfs.py")
            return
        
        # Teste de busca
        test_queries = [
            "Qual é o objetivo da universidade?",
            "Como funciona o sistema de avaliação?",
            "Quais são as disciplinas obrigatórias?",
        ]
        
        print(f"\n🔍 Teste de busca de similaridade:")
        for query in test_queries:
            results = db.similarity_search(query, k=1)
            if results:
                print(f"\n  Q: '{query}'")
                print(f"  ✅ Encontrado: {results[0].page_content[:100]}...")
                print(f"     Fonte: {results[0].metadata.get('source', 'N/A')}")
            else:
                print(f"\n  Q: '{query}'")
                print(f"  ❌ Nenhum resultado encontrado")
    
    except Exception as e:
        print(f"❌ Erro ao conectar no Chroma: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_chroma()
