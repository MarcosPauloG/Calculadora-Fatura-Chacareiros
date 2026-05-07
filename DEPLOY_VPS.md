# Deploy na VPS Hostinger (root ou /opt)

Este guia mostra comandos prontos para subir o sistema em uma VPS Hostinger usando Docker Compose.

## 1) Acessar a VPS

```bash
ssh root@SEU_IP
```

## 2) Escolher pasta de deploy

### Opção A (recomendada): `/opt/chacareiros-app`

```bash
mkdir -p /opt/chacareiros-app
cd /opt/chacareiros-app
```

### Opção B: `/root/chacareiros-app`

```bash
mkdir -p /root/chacareiros-app
cd /root/chacareiros-app
```

## 3) Enviar o projeto para a VPS

Você pode usar **git clone** ou **scp/rsync**.

### 3.1 Via Git (mais fácil para atualizações)

```bash
# na VPS
cd /opt/chacareiros-app
git clone <URL_DO_REPOSITORIO> .
```

### 3.2 Via SCP (se estiver local)

```bash
# no seu computador local (fora da VPS)
scp -r ./Calculadora-Fatura-Chacareiros/* root@SEU_IP:/opt/chacareiros-app/
```

### 3.3 Via rsync (mais rápido em updates)

```bash
# no seu computador local
rsync -avz --delete ./Calculadora-Fatura-Chacareiros/ root@SEU_IP:/opt/chacareiros-app/
```

## 4) Subir containers

```bash
# na VPS
cd /opt/chacareiros-app
docker compose up -d --build
```

## 5) Verificar status e logs

```bash
docker compose ps
docker compose logs -f --tail=200 web
docker compose logs -f --tail=200 api
```

## 6) Liberar portas no firewall (se necessário)

```bash
ufw allow 8090/tcp
ufw allow 8091/tcp
ufw status
```

## 7) Nginx Proxy Manager

Criar Proxy Host para o frontend:
- Domain: `chacareiros.x7q-prt99.cloud`
- Forward Hostname/IP: IP da VPS
- Forward Port: `8090`
- SSL: Let's Encrypt + Force SSL

API opcional separada:
- Domain: `api-chacareiros.x7q-prt99.cloud`
- Forward Port: `8091`

## 8) Atualizar versão (deploy contínuo manual)

### Se usa Git

```bash
cd /opt/chacareiros-app
git pull
docker compose up -d --build
```

### Se usa rsync/scp

```bash
# reenvie os arquivos e rode:
cd /opt/chacareiros-app
docker compose up -d --build
```

## 9) Comandos úteis

```bash
# reiniciar
cd /opt/chacareiros-app
docker compose restart

# parar
cd /opt/chacareiros-app
docker compose down

# parar e remover volumes (cuidado)
cd /opt/chacareiros-app
docker compose down -v
```
