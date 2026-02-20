from flask import Flask, request, jsonify

from bot.ai_bot import AIBot
from services.waha import Waha

app = Flask(__name__)

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    payload = data.get("payload", {}) or {}

    chat_id = payload.get("from")
    received_message = payload.get("body", "")
    is_group = isinstance(chat_id, str) and ('@g.us' in chat_id)

    if is_group:
        return jsonify({'status': 'success', 'message': 'Mensagem de grupo ignorada.'}), 200

    if not chat_id or not received_message:
        return jsonify({'status': 'success', 'message': 'Sem chat_id ou body.'}), 200

    waha = Waha()
    ai_bot = AIBot()

    try:
        waha.start_typing(chat_id=chat_id)
    except Exception:
        pass

    try:
        response_message = ai_bot.invoke(received_message)
        # limita tamanho
        if len(response_message) > 3000:
            response_message = response_message[:3000] + "\n\n(Resposta truncada.)"

        waha.send_message(chat_id=chat_id, message=response_message)
    finally:
        try:
            waha.stop_typing(chat_id=chat_id)
        except Exception:
            pass

    return jsonify({'status': 'success'}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)