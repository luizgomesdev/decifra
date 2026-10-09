# Deploy

A solução roda em uma instância EC2 na AWS, com a mesma composição de containers do ambiente local: Qdrant, Postgres, a API e o front já construído.

## O que está no ar

| Item | Valor |
|---|---|
| Instância | `i-0d69e72e3ea614507`, t3.small, us-east-1a |
| Interface | http://100.24.98.206 |
| API | http://100.24.98.206:8000 |
| Saúde | http://100.24.98.206:8000/health |

É um ambiente de demonstração acadêmica, com laudos sintéticos. Fica em HTTP, sem domínio e sem certificado, e é desligado depois da correção. Se o endereço não responder, a instância foi parada para não gerar custo.

## Como está montado

```
EC2 (Ubuntu 24.04, Docker)
├── web      nginx servindo o build do front na porta 80
├── api      FastAPI na porta 8000
├── qdrant   base vetorial, exposta só no loopback
└── postgres memória de conversa, exposta só no loopback
```

Os containers sobem com `restart: unless-stopped`, então voltam sozinhos depois de um reboot.

## Passos executados

```bash
# 1. Infraestrutura (da máquina local, com o perfil da AWS)
aws ec2 create-key-pair --key-name decifra-fiap        # chave salva em ~/.ssh
aws ec2 create-security-group --group-name decifra-fiap
#    portas 80 e 8000 abertas; 22 apenas para o IP do desenvolvedor
aws ec2 run-instances --instance-type t3.small --image-id <ubuntu-24.04>

# 2. Preparo da instância
sudo fallocate -l 2G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile

# 3. Código e segredos
rsync -az --exclude .git --exclude .venv --exclude node_modules ./ ubuntu@<ip>:~/decifra/
scp server.env ubuntu@<ip>:~/decifra/.env      # chave da OpenAI, senha do Postgres, origens

# 4. Subir
ssh ubuntu@<ip> 'cd decifra && docker compose -f compose.prod.yml up -d --build'

# 5. Ingestão dos laudos sintéticos, rodada da máquina local por um túnel
ssh -N -L 6333:localhost:6333 ubuntu@<ip> &
cd apps/api && QDRANT_URL=http://localhost:6333 uv run python ../../scripts/ingest.py
```

A ingestão roda de fora porque ela depende do Docling, que é pesado: o servidor só precisa responder, não converter PDF.

## Variáveis do servidor

O arquivo `.env` existe apenas na instância, com permissão 600, e segue `.env.deploy.example`:

| Variável | Para quê |
|---|---|
| `OPENAI_API_KEY` | chamadas ao modelo |
| `POSTGRES_PASSWORD` | senha do banco, gerada no deploy |
| `ALLOWED_ORIGINS` | origem que o navegador pode usar contra a API |
| `VITE_API_URL` | endereço da API embutido no build do front |

## Operação

```bash
docker compose -f compose.prod.yml ps          # estado dos containers
docker compose -f compose.prod.yml logs -f api # eventos JSON da API
curl -s localhost:8000/health | jq             # dependências
```
