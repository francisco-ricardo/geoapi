#!/usr/bin/env python3
"""
Demonstração interativa dos Schemas Pydantic.
"""

from app.schemas.link import LinkBase, LinkCreate, LinkResponse, LinkList
from pydantic import ValidationError
import json


def demo_schema_basics():
    """Demonstra conceitos básicos dos schemas."""
    print("=" * 60)
    print("🔍 DEMO: Schemas Pydantic - Conceitos Básicos")
    print("=" * 60)
    
    # 1. Criação básica
    print("\n1️⃣ CRIAÇÃO BÁSICA:")
    print("LinkBase() - sem dados")
    link_empty = LinkBase()
    print(f"   Resultado: {link_empty}")
    print(f"   road_name: {link_empty.road_name}")
    print(f"   speed_limit: {link_empty.speed_limit}")
    
    # 2. Criação com dados
    print("\n2️⃣ CRIAÇÃO COM DADOS:")
    print("LinkBase(road_name='Main St', speed_limit=35)")
    link_with_data = LinkBase(road_name="Main St", speed_limit=35)
    print(f"   Resultado: {link_with_data}")
    print(f"   road_name: {link_with_data.road_name}")
    print(f"   speed_limit: {link_with_data.speed_limit}")
    
    # 3. Serialização JSON
    print("\n3️⃣ SERIALIZAÇÃO PARA JSON:")
    json_data = link_with_data.model_dump()
    print(f"   .model_dump(): {json_data}")
    json_string = link_with_data.model_dump_json()
    print(f"   .model_dump_json(): {json_string}")


def demo_validation():
    """Demonstra validação automática."""
    print("\n\n" + "=" * 60)
    print("✅ DEMO: Validação Automática")
    print("=" * 60)
    
    # 1. Validação de tipos
    print("\n1️⃣ VALIDAÇÃO DE TIPOS:")
    try:
        print("LinkBase(speed_limit='texto_inválido')")
        LinkBase(speed_limit="texto_inválido")  # type: ignore  # Testando erro do Pydantic
    except ValidationError as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Validação de ranges
    print("\n2️⃣ VALIDAÇÃO DE RANGES:")
    try:
        print("LinkBase(speed_limit=300)  # Máximo é 200")
        LinkBase(speed_limit=300)
    except ValidationError as e:
        print(f"   ❌ Erro: {e}")
    
    try:
        print("LinkBase(length=-50)  # Deve ser >= 0")
        LinkBase(length=-50)
    except ValidationError as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Validação com sucesso
    print("\n3️⃣ VALIDAÇÃO COM SUCESSO:")
    print("LinkBase(speed_limit=65, length=1500.5)")
    valid_link = LinkBase(speed_limit=65, length=1500.5)
    print(f"   ✅ Sucesso: {valid_link}")


def demo_inheritance():
    """Demonstra herança entre schemas."""
    print("\n\n" + "=" * 60)
    print("🏗️ DEMO: Herança de Schemas")
    print("=" * 60)
    
    print("\n1️⃣ LinkCreate HERDA de LinkBase:")
    print("   LinkBase: road_name, length, road_type, speed_limit")
    print("   LinkCreate: + link_id, + geometry")
    
    link_create = LinkCreate(
        link_id=12345,
        road_name="Highway 101",
        length=2500.0,
        speed_limit=70
    )
    print(f"   Resultado: {link_create}")
    print(f"   link_id (novo): {link_create.link_id}")
    print(f"   road_name (herdado): {link_create.road_name}")
    
    print("\n2️⃣ Campo OBRIGATÓRIO vs OPCIONAL:")
    try:
        print("LinkCreate(road_name='Test') # Sem link_id obrigatório")
        LinkCreate.model_validate({"road_name": "Test"})  # Sem link_id
    except ValidationError as e:
        print(f"   ❌ Erro: {e}")


def demo_sqlalchemy_integration():
    """Demonstra integração com SQLAlchemy."""
    print("\n\n" + "=" * 60)
    print("🔗 DEMO: Integração com SQLAlchemy")
    print("=" * 60)
    
    # Simular um modelo SQLAlchemy
    class MockSQLAlchemyLink:
        def __init__(self):
            self.link_id = 54321
            self.road_name = "Database Road"
            self.length = 3000.0
            self.road_type = "highway"
            self.speed_limit = 80
            self.geometry = None
            self.speed_records_count = 2500
    
    mock_db_record = MockSQLAlchemyLink()
    
    print("1️⃣ CONVERSÃO DE MODELO SQLALCHEMY:")
    print(f"   Modelo DB: link_id={mock_db_record.link_id}")
    print(f"             road_name={mock_db_record.road_name}")
    print(f"             speed_records_count={mock_db_record.speed_records_count}")
    
    # Converter para schema Pydantic
    print("\n2️⃣ CONVERSÃO AUTOMÁTICA:")
    print("LinkResponse.model_validate(mock_db_record)")
    link_response = LinkResponse.model_validate(mock_db_record)
    print(f"   Schema: {link_response}")
    print(f"   JSON: {link_response.model_dump_json()}")


def demo_api_usage():
    """Demonstra uso em APIs."""
    print("\n\n" + "=" * 60)
    print("🌐 DEMO: Uso em APIs")
    print("=" * 60)
    
    print("1️⃣ ENTRADA DA API (Request):")
    # Simular dados que chegam via JSON na API
    json_input = {
        "link_id": 99999,
        "road_name": "API Street",
        "length": 800.0,
        "speed_limit": 45,
        "geometry": {
            "type": "LineString",
            "coordinates": [[-81.3792, 30.3322], [-81.3790, 30.3328]]
        }
    }
    print(f"   JSON recebido: {json_input}")
    
    # Validar automaticamente
    link_create = LinkCreate(**json_input)
    print(f"   ✅ Validado: {link_create}")
    
    print("\n2️⃣ SAÍDA DA API (Response):")
    # Simular resposta da API
    response_data = LinkResponse(
        link_id=99999,
        road_name="API Street", 
        length=800.0,
        speed_limit=45,
        speed_records_count=150
    )
    print(f"   Schema response: {response_data}")
    print(f"   JSON para cliente: {response_data.model_dump_json()}")
    
    print("\n3️⃣ LISTAGEM PAGINADA:")
    # Lista com múltiplos itens
    links = [
        LinkResponse(link_id=1, road_name="Road 1"),
        LinkResponse(link_id=2, road_name="Road 2"),
        LinkResponse(link_id=3, road_name="Road 3")
    ]
    
    link_list = LinkList(
        items=links,
        total=150,
        page=1,
        size=3,
        pages=50
    )
    print(f"   Lista: {len(link_list.items)} itens")
    print(f"   Paginação: página {link_list.page} de {link_list.pages}")
    print(f"   Total: {link_list.total} registros")


def demo_field_features():
    """Demonstra recursos avançados dos Fields."""
    print("\n\n" + "=" * 60)
    print("⚙️ DEMO: Recursos dos Fields")
    print("=" * 60)
    
    print("1️⃣ VALIDAÇÃO GE (>=) e LE (<=):")
    print("   speed_limit: ge=0, le=200  # Entre 0 e 200")
    print("   length: ge=0              # >= 0")
    
    print("\n2️⃣ DESCRIÇÕES E EXEMPLOS:")
    print("   description: Usado na documentação automática da API")
    print("   examples: Aparecem no Swagger/OpenAPI")
    
    print("\n3️⃣ DEFAULT VALUES:")
    print("   default=None: Campo opcional")
    print("   default=0: Campo com valor padrão")
    
    print("\n4️⃣ CONFIGDICT:")
    print("   from_attributes=True: Permite conversão de SQLAlchemy")
    print("   ConfigDict configura comportamento do modelo")


if __name__ == "__main__":
    demo_schema_basics()
    demo_validation()
    demo_inheritance()
    demo_sqlalchemy_integration()
    demo_api_usage()
    demo_field_features()
    
    print("\n\n" + "=" * 60)
    print("🎯 RESUMO DOS SCHEMAS")
    print("=" * 60)
    print("✅ LinkBase: Campos comuns (herança)")
    print("✅ LinkCreate: Para criar via API (+ link_id obrigatório)")
    print("✅ LinkUpdate: Para atualizar via API (tudo opcional)")
    print("✅ LinkResponse: Para retornar da API (+ campos calculados)")
    print("✅ LinkList: Para listagem paginada")
    print("\n🚀 Pronto para usar nos endpoints FastAPI!")
