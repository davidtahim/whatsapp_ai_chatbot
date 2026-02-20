from flask import Flask, request, jsonify
from collections import deque
from datetime import datetime, timedelta
import threading
import sys
import time

from services.waha import Waha

app = Flask(__name__)

# Flag para rastrear inicialização do AIBot
ai_bot_instance = None
ai_bot_ready = False
ai_bot_error = None
app_start_time = time.time()

def initialize_ai_bot():
    """Inicializa o AIBot em thread separada para não bloquear o health check"""
    global ai_bot_instance, ai_bot_ready, ai_bot_error
    print("[APP] Inicializando AIBot globalmente (em thread separada)...")
    try:
        from bot.ai_bot import AIBot
        ai_bot_instance = AIBot()
        ai_bot_ready = True
        print("[APP] ✅ AIBot global inicializado com sucesso!")
    except Exception as e:
        ai_bot_error = str(e)
        print(f"[APP] ❌ Erro ao inicializar AIBot: {e}", file=sys.stderr)
        ai_bot_ready = True  # Marca como pronto mesmo com erro (evita ficar esperando)

# Inicializar AIBot em background
ai_bot_thread = threading.Thread(target=initialize_ai_bot, daemon=True)
ai_bot_thread.start()

# Cache para evitar processar a mesma mensagem duas vezes
processed_messages = {}  # {message_id: timestamp}
MAX_CACHE_AGE = timedelta(minutes=5)

def is_duplicate_message(message_id):
    """Verifica se a mensagem já foi processada recentemente."""
    if message_id in processed_messages:
        age = datetime.now() - processed_messages[message_id]
        if age < MAX_CACHE_AGE:
            return True
        else:
            del processed_messages[message_id]
    return False

def mark_message_processed(message_id):
    """Marca a mensagem como processada."""
    processed_messages[message_id] = datetime.now()
    # Limpar mensagens antigas do cache
    if len(processed_messages) > 100:
        oldest_key = min(processed_messages, key=processed_messages.get)
        del processed_messages[oldest_key]

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    print(f"Received data: {data}")
    payload = data.get("payload", {}) or {}
    print(f"Payload: {payload}")

    # Obter ID da mensagem para deduplicação
    message_id = payload.get("id", "")
    chat_id = payload.get("from")
    received_message = payload.get("body", "")
    print(f"chat_id: {chat_id}, message_id: {message_id}, received_message: {received_message}")

    # Verificar se é duplicata
    if message_id and is_duplicate_message(message_id):
        print(f"[WEBHOOK] ⚠️  Mensagem duplicada ignorada (ID: {message_id})")
        return jsonify({'status': 'duplicate'}), 200

    # Marcar como processada IMEDIATAMENTE para evitar race condition
    if message_id:
        mark_message_processed(message_id)

    is_group = isinstance(chat_id, str) and ('@g.us' in chat_id)

    if is_group:
        return jsonify({'status': 'success', 'message': 'Mensagem de grupo ignorada.'}), 200

    if not chat_id or not received_message:
        return jsonify({'status': 'success', 'message': 'Sem chat_id ou body.'}), 200

    if ai_bot_instance is None:
        print(f"[WEBHOOK] ❌ AIBot não foi inicializado corretamente!")
        if ai_bot_error:
            return jsonify({'status': 'error', 'message': f'Bot não inicializado: {ai_bot_error}'}), 500
        else:
            # Ainda está inicializando em background
            return jsonify({'status': 'error', 'message': 'Bot ainda está inicializando, tente novamente em alguns segundos'}), 503

    waha = Waha()

    try:
        waha.start_typing(chat_id=chat_id)
    except Exception:
        pass

    try:
        print(f"[WEBHOOK] Invocando AIBot com pergunta: '{received_message}'")
        response_message = ai_bot_instance.invoke(received_message)
        print(f"[WEBHOOK] Resposta gerada: {response_message[:200]}...")
        
        # limita tamanho
        if len(response_message) > 1000:
            print(f"[WEBHOOK] Resposta truncada de {len(response_message)} para 1000 caracteres")
            response_message = response_message[:1000]

        print(f"[WEBHOOK] Enviando mensagem para {chat_id}")
        waha.send_message(chat_id=chat_id, message=response_message)
        print(f"[WEBHOOK] ✅ Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"[WEBHOOK] ❌ Erro ao processar mensagem: {e}")
        import traceback
        traceback.print_exc()
        try:
            waha.send_message(chat_id=chat_id, message=f"❌ Erro ao processar sua pergunta: {str(e)}")
        except:
            pass
    finally:
        try:
            waha.stop_typing(chat_id=chat_id)
        except Exception:
            pass

    return jsonify({'status': 'success'}), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check rápido - responde imediatamente sem esperar AIBot"""
    uptime = time.time() - app_start_time
    return jsonify({"status": "ok", "ai_bot_ready": ai_bot_ready, "uptime_seconds": round(uptime, 2)}), 200


@app.route("/", methods=["GET"])
def root():
    """Root endpoint para verificação básica"""
    return jsonify({"message": "WhatsApp AI Chatbot is running", "health": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)