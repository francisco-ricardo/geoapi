# API Management Commands Guide

## 🚀 Como Subir a API

### Cenários Diferentes

#### 1. **Primeira Vez / Setup Completo**
```bash
# Sobe containers, cria tabelas e ingere dados
make setup
```

#### 2. **Apenas Subir Containers (sem API rodando)**
```bash
# Sobe containers (PostgreSQL + container da API)
make start
```

#### 3. **Rodar a API com uvicorn**

```bash
# Rodar API em modo development (recomendado)
make run-api-dev

# Rodar API em modo básico
make run-api

# Rodar API em modo produção (4 workers)
make run-api-prod
```

## 🔧 Gerenciamento da API

### Verificar Status
```bash
# Verificar se API está respondendo
make check-api

# Status completo (container + API + endpoints)
make api-status
```

### Controlar Processo da API
```bash
# Parar processo uvicorn
make stop-api

# Reiniciar API
make restart-api
```

### Logs e Debug
```bash
# Ver logs dos containers
make logs

# Abrir shell no container da API
make shell
```

## 📋 Fluxo Típico de Desenvolvimento

### Primeira Vez
```bash
# 1. Setup completo
make setup

# 2. Verificar se está funcionando
make api-status
```

### Desenvolvimento Diário
```bash
# 1. Subir containers
make start

# 2. Rodar API em modo development
make run-api-dev

# 3. Fazer alterações no código (auto-reload ativo)

# 4. Testar
make test

# 5. Verificar API
make check-api
```

### Troubleshooting
```bash
# Se API não responder
make stop-api
make restart-api

# Se containers não estiverem rodando
make restart

# Ver logs para debug
make logs
```

## 🎯 Pontos de Acesso

Após `make run-api-dev`:

- **API Server**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

## ⚠️ Diferença dos Comandos

| Comando | O que faz |
|---------|-----------|
| `make start` | Sobe apenas os containers (DB + API container) |
| `make run-api` | Executa uvicorn dentro do container |
| `make run-api-dev` | Executa uvicorn com reload e debug |
| `make setup` | start + create-tables + ingest-data |

## 💡 Dicas

1. **Para desenvolvimento**: sempre use `make run-api-dev` para ter auto-reload
2. **Para testar**: use `make check-api` antes de fazer requests
3. **Para debug**: use `make logs` para ver o que está acontecendo
4. **Para limpar**: use `make stop` para parar tudo

## 🔄 Comandos Corrigidos

**Antes (inútil):**
```bash
make run-api  # Apenas imprimia mensagens
```

**Agora (funcional):**
```bash
make run-api      # Executa uvicorn
make run-api-dev  # Executa uvicorn com reload
make run-api-prod # Executa uvicorn com 4 workers
make api-status   # Mostra status completo
```
