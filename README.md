# GeoSpatial Links API

A robust geospatial REST API built with **FastAPI**, **SQLAlchemy**, **PostgreSQL/PostGIS**, and **Pydantic** for traffic data analysis and visualization.

## 🚀 Quick Start (For Interviewers)

### Prerequisites
- Docker and Docker Compose installed on your host machine
- Clone this repository

### Setup and Run
```bash
# 1. Start the containers (database + API)
make start

# 2. Complete setup (tables + data ingestion)
make setup

# 3. Access the API
# - API Server: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

### Alternative Commands
```bash
# Step by step setup
make start              # Start containers
make create-tables      # Create database tables
make ingest-data        # Load Parquet datasets

# Development commands
make logs              # View container logs
make shell             # Open shell in API container
make db-shell          # Open PostgreSQL shell
make test              # Run tests
make health-check      # Check system health
```

### Access Points
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

## � Technologies

- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Database**: PostgreSQL + PostGIS (with automatic table creation)
- **Geospatial**: GeoAlchemy2, PostGIS, GeoJSON
- **Testing**: pytest, TDD approach
- **DevOps**: Docker, DevContainer, automated setup

## � Project Structure

```
app/
├── core/
│   ├── config.py          # Configuration with Pydantic Settings
│   └── database.py        # Engine/session factory (SQLite/PostgreSQL)
├── models/
│   ├── link.py           # Road links model (with PostGIS geometry)
│   └── speed_record.py   # Speed measurements model
├── schemas/
│   ├── link.py           # Pydantic schemas for links
│   └── speed_record.py   # Pydantic schemas for speed records
├── api/v1/
│   └── links.py          # API endpoints implementation
└── services/             # Business logic layer

scripts/
├── setup/
│   └── complete_setup.py # Automated project setup
├── database/
│   └── create_tables.py  # Database initialization
├── demo/
│   ├── schemas_basic.py  # Basic schema demonstration
│   └── schemas_complete.py # Complete schema guide
└── testing/
    ├── run_tests.py      # Test runner
    ├── run_tests_by_category.py # Category-based tests
    └── test_endpoints.py # API endpoint testing

tests/
├── conftest.py           # Shared test fixtures
├── test_*.py            # Unit tests
└── test_models/         # Model-specific tests
```

## 🧪 Testing System

The project features a **comprehensive testing system** with multiple categories:

### Run Tests
```bash
# All tests
make test

# By category
python scripts/testing/run_tests_by_category.py basic    # No database required
python scripts/testing/run_tests_by_category.py schema   # Pydantic validation
python scripts/testing/run_tests_by_category.py database # PostgreSQL required
python scripts/testing/run_tests_by_category.py all      # Complete suite
```

### API Testing
```bash
# Test endpoints manually
python scripts/testing/test_endpoints.py
```

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
