# Diagnóstico: Mensagens não chegam

## Status dos Containers ✅
- Flask API (port 5000): Rodando
- WAHA (port 3000): Rodando

## Possíveis Causas

### 1️⃣ WAHA não está conectado ao WhatsApp ⚠️ **PROVÁVEL**

**Como verificar:**
- Acesse http://localhost:3000 no navegador
- Clique em "Scan QR Code"
- Veja se a sessão "default" mostra "CONNECTED"

Se não estiver conectado, o WAHA não recebe mensagens.

**Solução:**
```bash
# 1. Acesse o dashboard do WAHA
http://localhost:3000

# 2. Faça login com as credenciais do .env
Username: admin
Password: e418301513a74a1db27cd185d7c7dccb

# 3. Vá em "Sessions" e clique "Scan QR Code"
# 4. Escaneie com WhatsApp no seu celular
# 5. Aguarde conectar e volte ao dashboard
```

### 2️⃣ Webhook não está configurado no WAHA

**Como verificar:**
- Vá para http://localhost:3000/api/settings (se houver UI)
- Ou use curl:
```bash
curl http://localhost:3000/api/default/webhooks \
  -H "X-API-Key: 1234"
```

**Esperado:**
- Deve haver um webhook apontando para `http://api:5000/chatbot/webhook`
- O evento deve estar em: `message` ou `messages`

### 3️⃣ Testar o webhook manualmente

```bash
# Enviar um POST para simular uma mensagem chegando
curl -X POST http://localhost:5000/chatbot/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "from": "5521999999999@c.us",
      "body": "Olá"
    }
  }'
```

Se retornar `{"status": "success"}`, o webhook está funcionando.

### 4️⃣ Verificar logs em tempo real

```bash
# Terminal 1 - Logs da API
docker-compose logs -f api

# Terminal 2 - Logs do WAHA
docker-compose logs -f waha
```

Envie uma mensagem no WhatsApp e veja se aparece algo nos logs.

## Próximos Passos

1. ✅ Verificar se o WAHA está conectado ao WhatsApp
2. ✅ Confirmar webhook no dashboard do WAHA
3. ✅ Testar webhook manualmente com curl
4. ✅ Enviar mensagem real no WhatsApp e observar logs
