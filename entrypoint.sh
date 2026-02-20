#!/bin/bash

echo "🚀 Iniciando aplicação..."

# Verificar se há PDFs para ingerir
if [ -d "/app/data/pdfs" ] && [ "$(ls -A /app/data/pdfs)" ]; then
    echo "📄 PDFs encontrados. Iniciando ingestão..."
    
    # Verificar se a coleção já existe no Chroma
    if [ ! -f "/app/chroma_data/chroma.sqlite3" ]; then
        echo "🔄 Primeira execução detectada. Ingestando PDFs..."
        python /app/ingest_pdfs.py
        if [ $? -eq 0 ]; then
            echo "✅ Ingestão de PDFs concluída com sucesso!"
        else
            echo "❌ Erro na ingestão de PDFs, continuando mesmo assim..."
        fi
    else
        echo "✅ PDFs já foram ingestados. Pulando ingestão..."
    fi
else
    echo "⚠️  Nenhum PDF encontrado em /app/data/pdfs"
fi

echo "🌐 Iniciando Flask..."
exec flask run --host=0.0.0.0 --port=5000 --debug
