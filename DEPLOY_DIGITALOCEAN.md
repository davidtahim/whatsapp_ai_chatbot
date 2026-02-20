# 🚀 Guia de Deployment em Produção - DigitalOcean

## Opção 1: App Platform (Recomendado - Mais Fácil)

### Pré-requisitos
- Conta no [DigitalOcean](https://www.digitalocean.com/)
- Repositório GitHub com o código
- Variáveis de ambiente configuradas

### Passo 1: Preparar o Repositório
1. Faça push do seu código para GitHub
2. Certifique-se que tem `.env.example` (sem valores sensíveis)
3. Crie um `app.yaml` na raiz do projeto

### Passo 2: Criar `app.yaml`
```yaml
name: whatsapp-ai-chatbot
services:
- name: api
  github:
    repo: seu-usuario/whatsapp_ai_chatbot
    branch: main
  build_command: docker build -f Dockerfile -t api:latest .
  http_port: 5000
  envs:
  - key: GROQ_API_KEY
    scope: RUN_AND_BUILD_TIME
    value: ${GROQ_API_KEY}
  - key: GROQ_MODEL
    value: llama-3.1-8b-instant
  - key: WAHA_API_KEY
    value: ${WAHA_API_KEY}
  - key: WAHA_URL
    value: http://waha:3000
  - key: WAHA_SESSION
    value: default
  - key: WHATSAPP_HOOK_URL
    value: https://seu-app.ondigitalocean.app/chatbot/webhook
  - key: PDF_DIR
    value: /app/data/pdfs
  - key: CHROMA_DIR
    value: /app/chroma_data

- name: waha
  image:
    registry_type: DOCKER_HUB
    registry: devlikeapro/waha:latest
  http_port: 3000
  envs:
  - key: WAHA_API_KEY
    value: ${WAHA_API_KEY}
  - key: WAHA_SESSION
    value: default
  - key: WHATSAPP_HOOK_URL
    value: https://seu-app.ondigitalocean.app/chatbot/webhook
  - key: WHATSAPP_HOOK_EVENTS
    value: message

volumes:
- name: chroma-data
  source_type: DROPLET_FS
  mount_path: /app/chroma_data
- name: pdfs-data
  source_type: DROPLET_FS
  mount_path: /app/data/pdfs
```

### Passo 3: Deploy via DigitalOcean Console
1. Acesse [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Clique em "Create App"
3. Selecione seu repositório GitHub
4. Cole o conteúdo do `app.yaml`
5. Configure as variáveis de ambiente:
   - `GROQ_API_KEY`: Sua chave da API Groq
   - `WAHA_API_KEY`: Chave de segurança (qualquer valor)
6. Clique em "Deploy"

---

## Opção 2: Droplet + Docker (Mais Controle)

### Passo 1: Criar Droplet
1. Acesse [DigitalOcean Droplets](https://cloud.digitalocean.com/droplets)
2. Clique em "Create Droplet"
3. Configuração recomendada:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic ($4-6/mês)
   - **Region**: São Paulo ou mais próximo
   - **Add SSH Key**: Configure sua chave SSH

### Passo 2: Configurar Droplet
```bash
# 1. Conectar ao droplet via SSH
ssh root@seu_ip_do_droplet

# 2. Atualizar sistema
apt update && apt upgrade -y

# 3. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 5. Verificar instalação
docker --version
docker-compose --version
```

### Passo 3: Clonar Repositório e Configurar
```bash
# 1. Instalar Git
apt install git -y

# 2. Clonar projeto
cd /root
git clone https://github.com/seu-usuario/whatsapp_ai_chatbot.git
cd whatsapp_ai_chatbot

# 3. Criar arquivo .env com variáveis de produção
cat > .env << EOF
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=llama-3.1-8b-instant
HUGGINGFACE_API_KEY=sua_chave_huggingface

WAHA_API_KEY=sua_chave_segura
WAHA_DASHBOARD_USERNAME=admin
WAHA_DASHBOARD_PASSWORD=$(openssl rand -base64 32)
WHATSAPP_SWAGGER_USERNAME=admin
WHATSAPP_SWAGGER_PASSWORD=$(openssl rand -base64 32)
WAHA_URL=http://waha:3000
WAHA_SESSION=default
WHATSAPP_HOOK_URL=https://seu_dominio.com/chatbot/webhook
WHATSAPP_HOOK_EVENTS=message

PDF_DIR=/app/data/pdfs
CHROMA_DIR=/app/chroma_data
CHROMA_COLLECTION=uni7_pdfs
TOP_K=5
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
EOF
```

### Passo 4: Subir Containers em Background
```bash
# Iniciar containers
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f api
```

### Passo 5: Configurar Nginx (Reverse Proxy)
```bash
# 1. Instalar Nginx
apt install nginx -y

# 2. Criar configuração
cat > /etc/nginx/sites-available/whatsapp-bot << 'EOF'
server {
    listen 80;
    server_name seu_dominio.com;

    location /chatbot/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://localhost:5000;
    }
}
EOF

# 3. Ativar site
ln -s /etc/nginx/sites-available/whatsapp-bot /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# 4. Testar configuração
nginx -t

# 5. Reiniciar Nginx
systemctl restart nginx
```

### Passo 6: SSL/HTTPS com Let's Encrypt
```bash
# 1. Instalar Certbot
apt install certbot python3-certbot-nginx -y

# 2. Gerar certificado
certbot --nginx -d seu_dominio.com

# 3. Renovação automática já está configurada
systemctl status certbot.timer
```

### Passo 7: Configurar Domínio
1. Acesse seu registrador de domínio
2. Configure DNS A record apontando para o IP do Droplet
3. Espere propagação (até 24h)

---

## Configuração do WAHA em Produção

### 1. Conectar WhatsApp
1. Acesse `https://seu_dominio.com` (porta padrão do WAHA)
2. Faça login com as credenciais do `.env`
3. Escaneie o QR code com WhatsApp no celular
4. Confirme a conexão

### 2. Configurar Webhook
O webhook deve estar automaticamente configurado como:
```
URL: https://seu_dominio.com/chatbot/webhook
Eventos: message
```

---

## Monitoramento em Produção

### Ver Logs
```bash
# Logs em tempo real
docker-compose logs -f api

# Últimas 100 linhas
docker-compose logs api --tail 100

# Apenas erros
docker-compose logs api | grep ERROR
```

### Reiniciar Serviços
```bash
# Reiniciar apenas a API
docker-compose restart api

# Reiniciar tudo
docker-compose restart

# Rebuild e restart
docker-compose up --build -d
```

### Usar PM2 para Persistência (Alternativa)
```bash
# Instalar PM2
npm install -g pm2

# Criar script de inicialização
cat > start.sh << 'EOF'
#!/bin/bash
cd /root/whatsapp_ai_chatbot
docker-compose up -d
EOF

chmod +x start.sh

# Monitorar com PM2
pm2 start ./start.sh --name "whatsapp-bot"
pm2 save
pm2 startup
```

---

## Backup de PDFs e Dados

### Backup Automático
```bash
# Criar script de backup
cat > /root/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de PDFs
tar -czf $BACKUP_DIR/pdfs_$DATE.tar.gz /root/whatsapp_ai_chatbot/data/pdfs/

# Backup do Chroma
tar -czf $BACKUP_DIR/chroma_$DATE.tar.gz /root/whatsapp_ai_chatbot/chroma_data/

# Backup do .env
cp /root/whatsapp_ai_chatbot/.env $BACKUP_DIR/.env_$DATE

echo "Backup realizado: $DATE"
EOF

chmod +x /root/backup.sh

# Agendar backup diário (cron)
crontab -e
# Adicione a linha (backup às 2h da manhã):
# 0 2 * * * /root/backup.sh
```

---

## Checklist de Produção

- [ ] Domínio configurado
- [ ] SSL/HTTPS ativo
- [ ] Variáveis de ambiente configuradas
- [ ] WhatsApp conectado no WAHA
- [ ] Webhook testado (enviar mensagem de teste)
- [ ] Logs monitorados
- [ ] Backup automático configurado
- [ ] Firewall habilitado (DigitalOcean Firewall)

---

## Troubleshooting

### Webhook não é chamado
```bash
# Verificar se o WAHA está conectado
curl http://localhost:3000/api/sessions -H "X-API-Key: sua_chave"

# Deve retornar algo como:
# [{"name":"default","status":"WORKING",...}]
```

### Erro 502 Bad Gateway
```bash
# Verificar se os containers estão rodando
docker-compose ps

# Reiniciar
docker-compose restart
```

### PDFs não são carregados
```bash
# Recarregar PDFs
docker-compose exec api python ingest_pdfs.py

# Verificar Chroma
docker-compose exec api python test_chroma.py
```

---

## Custo Estimado (DigitalOcean)

- **Droplet Basic ($4-6/mês)**
- **Gerenciamento de domínio ($12/ano)**
- **Backup storage ($5/mês)**
- **Total: ~$10-15/mês**

---

## Próximos Passos

1. ✅ Deploy realizado
2. ✅ Testar com mensagens reais
3. ✅ Configurar monitoramento
4. ✅ Adicionar mais PDFs conforme necessário
5. ✅ Escalar para Kubernetes se precisar de alta disponibilidade
