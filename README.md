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

# Data validation
make validate-ingestion # Validate data ingestion integrity
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

## 🔍 Validação de Dados

### Validação da Integridade da Ingestão

O projeto inclui um sistema robusto de validação de dados para garantir a integridade após a ingestão:

```bash
# Validar integridade dos dados após ingestão
make validate-ingestion
```

#### O que é validado:

**1. Dados de Links:**
- Geometrias válidas (GeoJSON/WKT)
- Coordenadas consistentes (SRID 4326) 
- Campos obrigatórios preenchidos
- Unicidade dos link_ids

**2. Dados de Velocidade:**
- Referências válidas para links existentes
- Timestamps em formato correto (UTC)
- Valores de velocidade dentro de limites razoáveis
- Períodos de tempo categorizados corretamente

**3. Integridade Referencial:**
- Todos os speed_records referenciam links válidos
- Geometrias PostGIS válidas e consistentes
- SRID uniforme em todas as geometrias

**4. Consistência Estatística:**
- Contagens de registros esperadas
- Médias de velocidade por período coerentes
- Distribuição temporal adequada

#### Exemplo de Output:
```
[PASS] Link geometries validation passed
[PASS] Speed records validation passed  
[PASS] All speed records have valid link references
[PASS] All geometries use consistent SRID: 4326
[PASS] Average speed for AM Peak matches: 35.94 mph
[PASS] ALL VALIDATIONS PASSED - Data ingestion is accurate

*** Data integrity confirmed! The ingestion process worked correctly. ***
```

### Outros Comandos de Validação

```bash
make analyze-data      # Analisar datasets Parquet originais
make verify-db         # Verificar estado do banco de dados
make verify-postgis    # Verificar dados espaciais PostGIS
```

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

## 📚 Lessons Learned

### 🚀 Performance Optimization: Chunk Processing

Durante o desenvolvimento, implementamos **chunk processing** para otimizar a ingestão de dados:

#### **Problema Inicial**
- Datasets grandes (1.2M+ registros) causavam problemas de memória
- Processamento sequencial era lento para grandes volumes

#### **Solução Implementada**
```python
# Chunk processing otimizado
def process_links_chunked(df, chunk_size=1000):
    """Process links data in chunks to avoid memory issues"""
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        # Process each chunk separately
        chunk_data = prepare_link_data(chunk)
        insert_batch(session, Link, chunk_data)
        
def process_speed_records_chunked(df, chunk_size=5000):
    """Manual chunking for speed records processing"""
    total_records = len(df)
    
    for start_idx in range(0, total_records, chunk_size):
        end_idx = min(start_idx + chunk_size, total_records)
        chunk = df.iloc[start_idx:end_idx]
        
        # Process chunk with optimized batch insert
        process_chunk_data(chunk)
```

#### **Resultados Obtidos**
- ✅ **Uso de Memória**: Reduzido significativamente (chunks de 5K registros)
- ✅ **Performance**: Ingestão de 1.2M registros em ~7 minutos
- ✅ **Confiabilidade**: Zero falhas de memória ou timeouts
- ✅ **Monitoramento**: Progress tracking em tempo real

#### **Métricas de Performance**
```
Links: 100,924 registros em chunks de 1,000
Speed Records: 1,239,946 registros em chunks de 5,000
Tempo total: ~7 minutos
Taxa: ~3,000 registros/segundo
```

#### **Lições Aprendidas**
1. **Chunk Size Matters**: 5K registros = sweet spot entre memória e performance
2. **Batch Inserts**: SQLAlchemy bulk operations são 10x mais rápidas
3. **Memory Management**: Chunking evita OutOfMemory em datasets grandes
4. **Progress Tracking**: Feedback visual melhora UX durante ingestão
5. **Error Handling**: Chunks permitem retry granular em caso de falhas

### 🛠️ Technical Implementation

```python
# Otimização principal no script de ingestão
CHUNK_SIZE = 5000  # Testado e otimizado

# Loop principal otimizado
for start_idx in range(0, total_records, CHUNK_SIZE):
    chunk = df.iloc[start_idx:start_idx + CHUNK_SIZE]
    
    # Bulk insert com SQLAlchemy
    session.bulk_insert_mappings(SpeedRecord, chunk_data)
    session.commit()
    
    # Progress tracking
    print(f"Chunk {chunk_num}: {len(chunk_data)} records processed")
```

---
