#!/usr/bin/env python3
"""
Demonstração COMPLETA dos Schemas Pydantic
Mostra todos os aspectos dos schemas implementados no projeto.
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, '/workspace')

from app.schemas.link import LinkBase, LinkCreate, LinkUpdate, LinkResponse, LinkList
from app.schemas.speed_record import SpeedRecordBase, SpeedRecordCreate, SpeedRecordUpdate, SpeedRecord, SpeedRecordList
from pydantic import ValidationError

def interactive_demo():
    """Demonstração interativa completa."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SCHEMAS PYDANTIC - GUIA COMPLETO                         ║
║                                                                              ║
║ Os schemas Pydantic são a "ponte" entre sua API e seu banco de dados.       ║
║ Eles garantem que os dados estejam no formato correto e sejam válidos.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # PARTE 1: O QUE SÃO SCHEMAS PYDANTIC?
    print("\n🔍 1. O QUE SÃO SCHEMAS PYDANTIC?")
    print("-" * 50)
    print("""
Os schemas Pydantic são classes Python que definem:
✅ Estrutura dos dados (quais campos existem)
✅ Tipos de dados (int, str, float, datetime, etc.)
✅ Validação (regras que os dados devem seguir)
✅ Serialização (conversão para JSON)
✅ Documentação (descrições e exemplos)

Exemplo básico do seu projeto:
""")
    
    # Demonstração básica
    print("💡 Criando um Link simples:")
    simple_link = LinkBase(
        road_name="Rua das Flores",
        length=1250.5,
        speed_limit=50
    )
    print(f"   ✅ Criado: {simple_link}")
    print(f"   📊 JSON: {simple_link.model_dump_json()}")
    
    # PARTE 2: VALIDAÇÃO AUTOMÁTICA
    print("\n🛡️ 2. VALIDAÇÃO AUTOMÁTICA")
    print("-" * 50)
    print("Os schemas validam automaticamente os dados:")
    
    print("\n   ✅ DADOS VÁLIDOS:")
    try:
        valid_link = LinkCreate(
            link_id=12345,
            road_name="Avenida Paulista",
            length=2800.0,
            speed_limit=60
        )
        print(f"      Link criado: ID {valid_link.link_id}, {valid_link.road_name}")
    except ValidationError as e:
        print(f"      Erro inesperado: {e}")
    
    print("\n   ❌ DADOS INVÁLIDOS:")
    
    # Tipo inválido
    try:
        invalid_link = LinkCreate(
            link_id="não_é_número",  # type: ignore  # Testando erro Pydantic
            speed_limit=50
        )
    except ValidationError as e:
        print(f"      ❌ Tipo inválido: {e.errors()[0]['msg']}")
    
    # Valor fora do range
    try:
        invalid_link = LinkCreate(
            link_id=1,
            length=-100  # Não pode ser negativo (ge=0)
        )
    except ValidationError as e:
        print(f"      ❌ Valor inválido: {e.errors()[0]['msg']}")
    
    # Limite de velocidade muito alto
    try:
        invalid_link = LinkCreate(
            link_id=1,
            speed_limit=300  # Máximo é 200 (le=200)
        )
    except ValidationError as e:
        print(f"      ❌ Limite excedido: {e.errors()[0]['msg']}")
    
    # PARTE 3: TIPOS DE SCHEMAS NO SEU PROJETO
    print("\n🏗️ 3. TIPOS DE SCHEMAS NO SEU PROJETO")
    print("-" * 50)
    
    print("📝 LinkBase (classe pai - campos comuns):")
    print("   • road_name: str opcional")
    print("   • length: float opcional (>=0)")
    print("   • road_type: str opcional") 
    print("   • speed_limit: int opcional (0-200)")
    
    print("\n📝 LinkCreate (para criar novos links via API):")
    print("   • Herda tudo de LinkBase")
    print("   • + link_id: int OBRIGATÓRIO")
    print("   • + geometry: dict opcional (GeoJSON)")
    
    print("\n📝 LinkUpdate (para atualizar links existentes):")
    print("   • Herda de LinkBase")
    print("   • + geometry: dict opcional")
    print("   • TODOS os campos são opcionais (update parcial)")
    
    print("\n📝 LinkResponse (para retornar dados da API):")
    print("   • Herda de LinkBase")
    print("   • + link_id: int")
    print("   • + geometry: dict opcional")
    print("   • + speed_records_count: int opcional (campo calculado)")
    print("   • + ConfigDict(from_attributes=True) para SQLAlchemy")
    
    # Demonstração prática
    print("\n💡 EXEMPLO PRÁTICO:")
    
    # Criar um link
    create_data = {
        "link_id": 98765,
        "road_name": "BR-116",
        "length": 4500.0,
        "road_type": "highway",
        "speed_limit": 120,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-43.2075, -22.9028],
                [-43.2070, -22.9025],
                [-43.2065, -22.9022]
            ]
        }
    }
    
    create_schema = LinkCreate(**create_data)
    print(f"   ✅ LinkCreate: ID {create_schema.link_id}")
    print(f"      Nome: {create_schema.road_name}")
    print(f"      Tipo: {create_schema.road_type}")
    print(f"      Comprimento: {create_schema.length}m")
    
    # Simular atualização parcial
    update_data = {
        "speed_limit": 100,  # Só mudando o limite de velocidade
        "road_type": "arterial"  # E o tipo da via
    }
    
    update_schema = LinkUpdate(**update_data)
    print(f"\n   ✅ LinkUpdate (parcial):")
    print(f"      Novo limite: {update_schema.speed_limit}")
    print(f"      Novo tipo: {update_schema.road_type}")
    print(f"      Nome mantido: {update_schema.road_name}")  # None = não alterado
    
    # PARTE 4: SPEED RECORDS
    print("\n🚗 4. SCHEMAS DE SPEED RECORD")
    print("-" * 50)
    
    print("Os SpeedRecords representam medições de velocidade em links:")
    
    speed_data = {
        "link_id": 98765,
        "timestamp": datetime.now(),
        "speed_kph": 85.3,
        "period": "afternoon"
    }
    
    speed_record = SpeedRecordCreate(**speed_data)
    print(f"✅ SpeedRecord criado:")
    print(f"   Link: {speed_record.link_id}")
    print(f"   Velocidade: {speed_record.speed_kph} km/h")
    print(f"   Quando: {speed_record.timestamp.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Período: {speed_record.period}")
    
    # Validação de velocidade
    print(f"\n🛡️ Validação de velocidade (0-300 km/h):")
    
    try:
        speed_too_fast = SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=400  # Muito rápido!
        )
    except ValidationError as e:
        print(f"   ❌ Velocidade muito alta: {e.errors()[0]['msg']}")
    
    try:
        speed_negative = SpeedRecordCreate(
            link_id=1,
            timestamp=datetime.now(),
            speed_kph=-50  # Negativa!
        )
    except ValidationError as e:
        print(f"   ❌ Velocidade negativa: {e.errors()[0]['msg']}")
    
    # PARTE 5: INTEGRAÇÃO COM FASTAPI
    print("\n🚀 5. USO COM FASTAPI")
    print("-" * 50)
    
    print("""
Como os schemas serão usados nos endpoints da API:

@app.post("/links/", response_model=LinkResponse)
async def create_link(link: LinkCreate, db: Session = Depends(get_db)):
    # link já vem validado pelo Pydantic!
    db_link = Link(
        link_id=link.link_id,
        road_name=link.road_name,
        length=link.length,
        # ... outros campos
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    
    # Conversão automática SQLAlchemy -> Pydantic
    return LinkResponse.model_validate(db_link)

@app.put("/links/{link_id}", response_model=LinkResponse)  
async def update_link(link_id: int, link: LinkUpdate, db: Session = Depends(get_db)):
    # Apenas campos não-None serão atualizados
    db_link = db.query(Link).filter(Link.link_id == link_id).first()
    
    update_data = link.model_dump(exclude_unset=True)  # Só campos fornecidos
    for field, value in update_data.items():
        setattr(db_link, field, value)
    
    db.commit()
    return LinkResponse.model_validate(db_link)
""")
    
    # PARTE 6: PAGINAÇÃO
    print("\n📄 6. SCHEMAS DE PAGINAÇÃO")
    print("-" * 50)
    
    # Simular alguns links para paginação
    sample_links = []
    for i in range(1, 6):
        link = LinkResponse(
            link_id=i,
            road_name=f"Rua {i}",
            length=1000.0 + i * 100,
            road_type="residential",
            speed_limit=30,
            speed_records_count=i * 10
        )
        sample_links.append(link)
    
    # Criar lista paginada
    paginated_list = LinkList(
        items=sample_links,
        total=147,  # Total de links no banco
        page=1,     # Página atual
        size=5,     # Itens por página
        pages=30    # Total de páginas
    )
    
    print(f"✅ Lista paginada criada:")
    print(f"   📊 Total de links: {paginated_list.total}")
    print(f"   📄 Página atual: {paginated_list.page} de {paginated_list.pages}")
    print(f"   📝 Links nesta página: {len(paginated_list.items)}")
    
    for link in paginated_list.items:
        print(f"      • {link.road_name} (ID: {link.link_id}) - {link.speed_records_count} registros")
    
    # PARTE 7: RECURSOS AVANÇADOS
    print("\n⚙️ 7. RECURSOS AVANÇADOS DOS SCHEMAS")
    print("-" * 50)
    
    print("🔧 Field() - Configuração avançada de campos:")
    print("""
speed_limit: Optional[int] = Field(
    default=None,                    # Valor padrão
    ge=0,                           # >= 0 (greater or equal)
    le=200,                         # <= 200 (less or equal)
    description="Speed limit in mph", # Para documentação
    examples=[35]                    # Exemplos no Swagger
)
""")
    
    print("🔧 ConfigDict - Configuração do modelo:")
    print("""
model_config = ConfigDict(
    from_attributes=True,    # Permite conversão de SQLAlchemy
    validate_assignment=True # Valida também em atribuições
)
""")
    
    print("🔧 Conversão automática de tipos:")
    demo_conversion = LinkCreate(
        link_id="12345",      # type: ignore  # String -> int
        length="1500.75",     # type: ignore  # String -> float
        speed_limit="60"      # type: ignore  # String -> int
    )
    print(f"   ✅ '12345' -> {demo_conversion.link_id} ({type(demo_conversion.link_id).__name__})")
    print(f"   ✅ '1500.75' -> {demo_conversion.length} ({type(demo_conversion.length).__name__})")
    print(f"   ✅ '60' -> {demo_conversion.speed_limit} ({type(demo_conversion.speed_limit).__name__})")
    
    # PARTE 8: PRÓXIMOS PASSOS
    print("\n🎯 8. PRÓXIMOS PASSOS")
    print("-" * 50)
    
    print("""
Agora que você entende os schemas, os próximos passos são:

1. 🚀 Criar endpoints FastAPI que usam estes schemas:
   • POST /links/ (usando LinkCreate)
   • GET /links/{id} (retornando LinkResponse)  
   • PUT /links/{id} (usando LinkUpdate)
   • GET /links/ (retornando LinkList)

2. 🔧 Expandir validações:
   • Validação mais específica de geometria GeoJSON
   • Validação de códigos de período (morning, afternoon, etc.)
   • Validação de tipos de via (arterial, highway, etc.)

3. 📊 Schemas para dados Parquet:
   • Validação de dados de ingestão em lote
   • Transformação de dados geoespaciais

4. 🗺️ Integração com Mapbox:
   • Schemas para configuração de mapas
   • Validação de estilos e camadas

5. 📚 Documentação automática:
   • OpenAPI/Swagger gerado automaticamente
   • Exemplos e descrições nos endpoints
""")
    
    print("\n" + "="*80)
    print("🎉 SCHEMAS PYDANTIC FUNCIONANDO PERFEITAMENTE!")
    print("   Sua base está sólida para construir a API geoespacial! 🗺️")
    print("="*80)

if __name__ == "__main__":
    interactive_demo()
