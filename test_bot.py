#!/usr/bin/env python
"""Script para testar o AIBot e sua capacidade de recuperar contexto."""

from bot.ai_bot import AIBot

# Testes de perguntas
test_questions = [
    "O que é uma aula híbrida?",
    "Como acesso o Portal do Aluno?",
    "Qual é o objetivo da UNI7?",
    "O que você sabe sobre a universidade?",
]

print("🤖 Testando AIBot - Recuperação de Contexto\n")
print("=" * 70)

bot = AIBot()

for question in test_questions:
    print(f"\n❓ Pergunta: {question}")
    
    # Teste 1: Verificar contexto recuperado
    context = bot._retrieve_context(question)
    
    if not context:
        print("   ⚠️  CONTEXTO VAZIO!")
    else:
        print(f"   ✅ Contexto recuperado ({len(context)} caracteres)")
        lines = context.split('\n')[:3]
        for line in lines:
            if line.strip():
                print(f"      📄 {line[:70]}...")
    
    # Teste 2: Invocar o bot
    print(f"   ⏳ Aguardando resposta do bot...")
    try:
        response = bot.invoke(question)
        print(f"   💬 Resposta: {response[:200]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("✅ Teste completado!")
