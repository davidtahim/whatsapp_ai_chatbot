import requests
import os


class Waha:

    def __init__(self):
        self.__api_url = os.getenv('WAHA_URL', 'http://waha:3000')
        self.__api_key = os.getenv('WAHA_API_KEY')

    def _get_headers(self):
        headers = {
            'Content-Type': 'application/json',
        }
        if self.__api_key:
            headers['X-API-Key'] = self.__api_key
        return headers

    def send_message(self, chat_id, message):
        try:
            url = f'{self.__api_url}/api/sendText'
            headers = self._get_headers()
            payload = {
                'session': 'default',
                'chatId': chat_id,
                'text': message,
            }
            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def get_history_messages(self, chat_id, limit):
        url = f'{self.__api_url}/api/default/chats/{chat_id}/messages?limit={limit}&downloadMedia=false'
        headers = self._get_headers()
        try:
            response = requests.get(
                url=url,
                headers=headers,
                timeout=10
            )
            print(f"WAHA API Response Status: {response.status_code}")
            print(f"WAHA API Response Headers: {dict(response.headers)}")

            if response.status_code != 200:
                print(f"Erro na API WAHA: {response.status_code} - {response.text}")
                return []

            data = response.json()
            print(f"Tipo de dados retornados: {type(data)}")
            print(f"Dados retornados: {data}")

            # Verificar se é uma lista ou dicionário
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Se for um dicionário, pode ter uma chave 'messages' ou similar
                return data.get('messages', data.get('data', []))
            else:
                print(f"Formato inesperado de resposta: {type(data)}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Erro de requisição para WAHA: {e}")
            return []
        except ValueError as e:
            print(f"Erro ao fazer parse do JSON: {e}")
            return []

    def start_typing(self, chat_id):
        try:
            url = f'{self.__api_url}/api/startTyping'
            headers = self._get_headers()
            payload = {
                'session': 'default',
                'chatId': chat_id,
            }
            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"Erro ao iniciar digitação: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro ao iniciar digitação: {e}")

    def stop_typing(self, chat_id):
        try:
            url = f'{self.__api_url}/api/stopTyping'
            headers = self._get_headers()
            payload = {
                'session': 'default',
                'chatId': chat_id,
            }
            response = requests.post(
                url=url,
                json=payload,
                headers=headers,
                timeout=10
            )
            if response.status_code != 200:
                print(f"Erro ao parar digitação: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro ao parar digitação: {e}")
