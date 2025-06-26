# GeoAPI - API Geoespacial para Avaliação Técnica

Uma API REST geoespacial construída com **FastAPI**, **SQLAlchemy**, **PostgreSQL/PostGIS**, **Pandas**, e **Parquet** para análise e visualização de dados de tráfego urbano.

## 🚀 Tecnologias

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Banco de Dados**: PostgreSQL + PostGIS (produção), SQLite (desenvolvimento/testes)
- **Análise de Dados**: Pandas, Parquet
- **Geoespacial**: GeoAlchemy2, PostGIS, Mapbox
- **Testes**: pytest, TDD
- **DevOps**: Docker, DevContainer

## 📋 Estrutura do Projeto

```
app/
├── core/
│   ├── config.py          # Configuração com Pydantic Settings
│   └── database.py        # Factory para engine/session (SQLite/PostgreSQL)
├── models/
│   ├── link.py           # Modelo de links viários (com geometry)
│   └── speed_record.py   # Modelo de registros de velocidade
├── api/v1/               # Endpoints da API (a implementar)
├── schemas/              # Schemas Pydantic (a implementar)
└── services/             # Lógica de negócio (a implementar)

tests/
├── conftest.py                    # Fixtures compartilhadas
├── test_config.py                 # Testes de configuração
├── test_database.py               # Testes do database factory
├── simplified_models.py           # Modelos simplificados (sem PostGIS)
├── test_simplified_models.py      # Testes dos modelos simplificados
└── test_models/
    ├── test_link.py              # Testes do modelo Link
    └── test_speed_record.py      # Testes do modelo SpeedRecord

run_tests.py                       # Script inteligente para execução de testes
```

## 🧪 Sistema de Testes

O projeto possui um **sistema de testes híbrido** que suporta tanto desenvolvimento local (SQLite) quanto ambiente de produção (PostgreSQL/PostGIS):

### Executar Testes (Desenvolvimento Local)

```bash
# Executa apenas testes compatíveis com SQLite (recomendado para TDD)
python run_tests.py --sqlite

# Mostra ajuda detalhada sobre os testes
python run_tests.py --help-tests
```

### Executar Todos os Testes (Produção)

```bash
# Executa TODOS os testes (requer PostgreSQL/PostGIS)
python run_tests.py --all
```

### 📊 Cobertura de Testes

- **24 testes** compatíveis com SQLite (desenvolvimento local)
- **Cobertura completa** da lógica de negócio dos modelos
- **Testes de configuração** com variáveis de ambiente
- **Testes de database factory** com cache e health checks
- **Testes isolados** para PostGIS (apenas em ambiente PostgreSQL)

### 🎯 Estratégia de Testes

1. **Modelos Simplificados**: Versões dos modelos sem geometria para testes com SQLite
2. **Testes de Estrutura**: Validam campos, relacionamentos e métodos sem banco
3. **Testes de Integração**: Executados apenas em ambiente PostgreSQL/PostGIS
4. **TDD Friendly**: Todos os testes essenciais funcionam localmente

## ⚙️ Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Database
DATABASE_URL="postgresql://user:pass@localhost:5432/geoapi"
DATABASE_URL_TEST="sqlite:///./test.db"

# API
API_TITLE="GeoAPI"
API_VERSION="1.0.0"
DEBUG=true

# Dados
MAPBOX_TOKEN="pk.your_token_here"  # Opcional
```

### DevContainer

O projeto está configurado para usar **DevContainer** com todas as dependências:

```bash
# Inicia o ambiente de desenvolvimento
docker-compose -f docker-compose-dev.yml up -d
```

## 🔧 Desenvolvimento

### 1. Configurar Ambiente

```bash
# Instalar dependências
pip install -r requirements-dev.txt

# Configurar Python environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 2. Executar Testes

```bash
# Desenvolvimento local (SQLite)
python run_tests.py --sqlite

# Ambiente completo (PostgreSQL)
python run_tests.py --all
```

### 3. Estrutura dos Modelos

#### Link (Links Viários)
```python
class Link(Base):
    id: int (PK)
    link_id: str (único)
    road_name: str (opcional)
    geometry: Geometry (Point/LineString, nullable para testes)
    speed_records: relationship -> SpeedRecord[]
```

#### SpeedRecord (Registros de Velocidade)
```python
class SpeedRecord(Base):
    id: int (PK)
    link_id: int (FK -> Link.id)
    timestamp: datetime
    speed_kph: float
    period: str (morning/afternoon/evening/night)
    link: relationship -> Link
```

## 📈 Próximos Passos

- [ ] Implementar endpoints FastAPI (`/api/v1/`)
- [ ] Criar schemas Pydantic para serialização
- [ ] Implementar serviços de ingestão de dados Parquet
- [ ] Desenvolver notebook Jupyter para análise com Mapbox
- [ ] Adicionar testes de integração da API
- [ ] Configurar CI/CD com GitHub Actions

## 🏗️ Arquitetura

O projeto segue os princípios de **Clean Architecture**, **SOLID**, e **KISS**:

- **Factory Pattern** para database connections
- **Dependency Injection** para configuração
- **Repository Pattern** (a implementar)
- **Clean Code** com tipagem forte
- **TDD** com cobertura abrangente

## 📚 Documentação

- **FastAPI**: Documentação automática em `/docs` (Swagger)
- **Modelos**: Documentados com docstrings e type hints
- **Testes**: Casos de teste descritivos e bem organizados

---

**Status Atual**: ✅ Base sólida implementada, pronto para desenvolvimento da API
