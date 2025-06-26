# Sistema de Testes - Documentação Técnica

## 🎯 Visão Geral

O projeto GeoAPI implementa um **sistema de testes híbrido** que resolve o problema da incompatibilidade entre PostGIS/GeoAlchemy2 e SQLite, permitindo TDD eficiente durante o desenvolvimento local.

## 🏗️ Arquitetura de Testes

### Duas Camadas de Testes

1. **Testes SQLite-Compatible** (Desenvolvimento Local)
   - ✅ Modelos simplificados sem geometria
   - ✅ Toda lógica de negócio dos modelos
   - ✅ Configuração e database factory
   - ✅ Relacionamentos e validações
   - ✅ Execução rápida e confiável

2. **Testes PostGIS-Dependent** (Ambiente PostgreSQL)
   - 🔶 Operações geoespaciais reais
   - 🔶 Índices espaciais
   - 🔶 Consultas com geometria
   - 🔶 Integração completa

### Estratégia de Modelos

#### Modelos Principais (`app/models/`)
```python
# link.py - Modelo completo com PostGIS
class Link(Base):
    geometry = Column(Geometry('POINT', srid=4326), nullable=True)  # nullable para testes
    
# speed_record.py - Relacionamento com Link
class SpeedRecord(Base):
    link_id = Column(Integer, ForeignKey('links.id'))
```

#### Modelos Simplificados (`tests/simplified_models.py`)
```python
# Versões sem geometria para testes SQLite
class SimplifiedLink(TestBase):
    # Todos os campos exceto geometry
    
class SimplifiedSpeedRecord(TestBase):
    # Relacionamento mantido
```

## 📊 Cobertura de Testes

### Testes Compatíveis com SQLite (24 testes)

| Categoria | Testes | Descrição |
|-----------|--------|-----------|
| **Configuração** | 6 | Pydantic Settings, env vars, caching |
| **Modelos Simplificados** | 9 | CRUD, relacionamentos, validações |
| **Database Factory** | 5 | Engine/session caching, health checks |
| **Estrutura de Modelos** | 4 | Tablenames, campos, relacionamentos |

### Testes Dependentes de PostGIS

| Categoria | Descrição |
|-----------|-----------|
| **Operações Geoespaciais** | Geometria, índices espaciais |
| **Integração Completa** | Testes end-to-end com PostgreSQL |
| **Performance** | Consultas espaciais otimizadas |

## 🔧 Ferramentas de Teste

### Script Principal: `run_tests.py`

```bash
# Desenvolvimento local (recomendado)
python run_tests.py --sqlite

# Ambiente completo
python run_tests.py --all

# Ajuda detalhada
python run_tests.py --help-tests
```

### Fixtures Compartilhadas (`conftest.py`)

```python
@pytest.fixture
def settings():
    """Configuração para testes"""

@pytest.fixture
def test_db():
    """Database SQLite para testes"""

@pytest.fixture  
def test_db_simple():
    """Database com modelos simplificados"""

@pytest.fixture
def sample_link():
    """Link de exemplo para testes"""
```

## 🎯 Benefícios da Arquitetura

### ✅ Vantagens

1. **TDD Eficiente**: Todos os testes essenciais rodam localmente
2. **Feedback Rápido**: 24 testes em ~0.24s
3. **Zero Setup**: Não precisa configurar PostgreSQL para desenvolvimento
4. **Cobertura Completa**: Toda lógica de negócio testada
5. **CI/CD Friendly**: Testes separados por ambiente

### 🎨 Padrões Implementados

1. **Factory Pattern**: Database connection com cache
2. **Test Doubles**: Modelos simplificados como substitutos
3. **Dependency Injection**: Fixtures parametrizáveis
4. **Clean Test Architecture**: Separação clara de responsabilidades

## 📝 Casos de Uso

### Desenvolvimento Local (TDD)
```bash
# Ciclo Red-Green-Refactor
python run_tests.py --sqlite
# Implementa funcionalidade
python run_tests.py --sqlite
# Refatora
python run_tests.py --sqlite
```

### CI/CD Pipeline
```yaml
# GitHub Actions exemplo
test-local:
  run: python run_tests.py --sqlite

test-integration:
  services:
    postgres:
      image: postgis/postgis
  run: python run_tests.py --all
```

### Debugging
```bash
# Teste específico com debug
pytest tests/test_simplified_models.py::TestSimplifiedLinkModel::test_link_creation -v -s

# Cobertura de código
pytest tests/test_simplified_models.py --cov=app/models --cov-report=html
```

## 🔄 Fluxo de Desenvolvimento

1. **Escreve teste** (modelo simplificado)
2. **Implementa lógica** (modelo principal)
3. **Valida localmente** (`--sqlite`)
4. **Testa integração** (`--all` em ambiente PostgreSQL)
5. **Deploy seguro**

## 📚 Referências Técnicas

- **pytest**: Framework de testes Python
- **SQLAlchemy 2.0**: ORM com suporte híbrido SQLite/PostgreSQL
- **GeoAlchemy2**: Extensão espacial para SQLAlchemy
- **Pydantic v2**: Validação e configuração
- **PostGIS**: Extensão espacial para PostgreSQL

---

**Resultado**: Sistema de testes robusto que suporta desenvolvimento ágil com TDD e integração confiável em produção.
