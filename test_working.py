#!/usr/bin/env python3
"""
Script para executar apenas os testes que funcionam com SQLite.
Exclui testes que dependem de PostGIS/GeoAlchemy2.
"""
import subprocess
import sys

def run_working_tests():
    """Execute apenas os testes que funcionam com SQLite."""
    
    # Testes que funcionam perfeitamente com SQLite
    working_tests = [
        # Configuração
        "tests/test_config.py",
        
        # Modelos simplificados (sem PostGIS)
        "tests/test_simplified_models.py",
        
        # Testes de database que não dependem de PostGIS
        "tests/test_database.py::TestDatabaseFactory::test_get_engine_caching",
        "tests/test_database.py::TestDatabaseFactory::test_get_session_factory_caching", 
        "tests/test_database.py::TestDatabaseFactory::test_health_check_success",
        "tests/test_database.py::TestDatabaseFactory::test_health_check_failure",
        "tests/test_database.py::TestDatabaseFactory::test_reset_database_state",
        
        # Testes de estrutura dos modelos (sem operações de banco)
        "tests/test_models/test_link.py::TestLinkModel::test_link_tablename",
        "tests/test_models/test_link.py::TestLinkModel::test_link_creation_structure",
        "tests/test_models/test_speed_record.py::TestSpeedRecordModel::test_speed_record_tablename",
        "tests/test_models/test_speed_record.py::TestSpeedRecordModel::test_speed_record_structure",
    ]
    
    print("🧪 Executando testes que funcionam com SQLite...\n")
    
    for test in working_tests:
        print(f"📋 {test}")
    
    print(f"\n🚀 Executando {len(working_tests)} testes...\n")
    
    # Executar testes
    cmd = ["python", "-m", "pytest"] + working_tests + ["-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print(f"\n✅ Todos os {len(working_tests)} testes passaram com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alguns testes falharam (código de saída: {e.returncode})")
        return False

def run_postgis_tests():
    """Lista os testes que precisam de PostGIS (apenas informativo)."""
    
    postgis_tests = [
        # Testes que dependem de PostGIS
        "tests/test_database.py::TestDatabaseFactory::test_get_db_dependency_generator",
        "tests/test_database.py::TestDatabaseFactory::test_get_db_session_direct", 
        "tests/test_database.py::TestTableManagement::*",
        "tests/test_database.py::TestDatabaseIntegration::*",
        "tests/test_models/test_link.py::TestLinkDatabaseOperations::*",
        "tests/test_models/test_speed_record.py::TestSpeedRecordDatabaseOperations::*",
    ]
    
    print("\n📝 Testes que precisam de PostgreSQL/PostGIS:")
    for test in postgis_tests:
        print(f"   🔶 {test}")
    
    print("\n💡 Estes testes devem ser executados apenas em ambiente PostgreSQL/PostGIS real.")

if __name__ == "__main__":
    print("=" * 80)
    print("🔬 GeoAPI - Teste Inteligente (SQLite Compatible)")
    print("=" * 80)
    
    success = run_working_tests()
    run_postgis_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 Status: TODOS OS TESTES COMPATÍVEIS PASSARAM!")
        print("✅ Projeto pronto para desenvolvimento da API")
    else:
        print("⚠️  Status: Alguns testes falharam")
        print("🔍 Revise os erros acima")
    
    print("=" * 80)
    
    sys.exit(0 if success else 1)
