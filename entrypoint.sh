#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

print("🚀 Iniciando aplicação...")

# Verificar se há PDFs para ingerir
pdfs_dir = Path("/app/data/pdfs")
chroma_db = Path("/app/chroma_data/chroma.sqlite3")

if pdfs_dir.exists() and any(pdfs_dir.iterdir()):
    print("📄 PDFs encontrados. Iniciando ingestão...")
    
    if not chroma_db.exists():
        print("🔄 Primeira execução detectada. Ingestando PDFs...")
        try:
            result = subprocess.run([sys.executable, "/app/ingest_pdfs.py"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ingestão de PDFs concluída com sucesso!")
            else:
                print(f"❌ Erro na ingestão de PDFs: {result.stderr}")
                print("Continuando mesmo assim...")
        except Exception as e:
            print(f"❌ Falha ao executar ingestão: {e}")
    else:
        print("✅ PDFs já foram ingestados. Pulando ingestão...")
else:
    print("⚠️  Nenhum PDF encontrado em /app/data/pdfs")

print("🌐 Iniciando Gunicorn (WSGI server)...")
os.execvp(sys.executable, [sys.executable, "-m", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "app:app"])

