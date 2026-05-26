# Calculadora de Fatura dos Chacareiros

MVP web responsivo (tema claro/escuro) com backend Python para:
- lançamento de leituras por data única (aplica para todos);
- cálculo automático de rateio;
- login por usuário/senha com troca obrigatória no primeiro acesso;
- painel admin para reset de senha.

## Fluxo solicitado

1. Definir **uma data** e referência do mês uma única vez.
2. Preencher por chacareiro apenas leitura e foto (URL/arquivo no Drive).
3. Salvar em lote.
4. Calcular rateio com base na fatura do geral.

## Usuários iniciais

Senha padrão de 1º acesso para usuários: `Chacara2026` (troca obrigatória).

- salvador
- christirson
- vidal
- milka
- girley
- fernando
- osmair
- weverton
- luciane
- paulo

Admin:
- usuário: `admin`
- senha: `Admin2026`

## n8n + Google Drive

O sistema salva `foto_url` por chacareiro e aceita `n8n_webhook_url` no envio em lote.
Estratégia recomendada:
- app envia metadados (nome, leitura, data, referencia, foto_url);
- n8n recebe e move/copia arquivo para pasta padrão no Drive;
- sistema evita guardar imagens na VPS.

## API principal

- `POST /api/login`
- `POST /api/change-password`
- `POST /api/admin/reset-password`
- `POST /api/readings/bulk`
- `POST /api/rateio`
- `GET /health`
