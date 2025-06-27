#!/usr/bin/env python3
"""
Script principal para executar testes no projeto GeoAPI.
"""
import subprocess
import sys
import argparse


def run_sqlite_tests():
    """Execute apenas os testes que funcionam com SQLite."""
    
    working_tests = [
        # Configuração
        "tests/test_config.py",
        
        # Schemas Pydantic
        "tests/test_schemas_link.py",
        
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
    
    print("🧪 Executando testes compatíveis com SQLite...\n")
    
    for test in working_tests:
        print(f"📋 {test}")
    
    print(f"\n🚀 Executando {len(working_tests)} testes...\n")
    
    cmd = ["python", "-m", "pytest"] + working_tests + ["-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print(f"\n✅ Todos os {len(working_tests)} testes passaram!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alguns testes falharam (código de saída: {e.returncode})")
        return False


def run_all_tests():
    """Execute todos os testes (requer PostgreSQL/PostGIS)."""
    
    print("🧪 Executando TODOS os testes (requer PostgreSQL/PostGIS)...\n")
    print("⚠️  ATENÇÃO: Este comando falhará se não estiver usando PostgreSQL/PostGIS!\n")
    
    cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, check=True, cwd="/workspace")
        print("\n✅ Todos os testes passaram!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Alguns testes falharam (código de saída: {e.returncode})")
        print("💡 Use 'python run_tests.py --sqlite' para executar apenas testes compatíveis com SQLite")
        return False


def show_help():
    """Mostra informações sobre os testes disponíveis."""
    
    print("=" * 80)
    print("🔬 GeoAPI - Guia de Testes")
    print("=" * 80)
    print()
    print("📋 COMANDOS DISPONÍVEIS:")
    print()
    print("  python run_tests.py --sqlite")
    print("    ✅ Executa apenas testes compatíveis com SQLite")
    print("    🔧 Ideal para desenvolvimento local e TDD")
    print("    📊 24 testes cobrem toda a lógica de negócio")
    print()
    print("  python run_tests.py --all")
    print("    🔶 Executa TODOS os testes (requer PostgreSQL/PostGIS)")
    print("    🐘 Deve ser usado apenas em ambiente com PostgreSQL/PostGIS")
    print("    🚫 Falhará se usado com SQLite")
    print()
    print("  python run_tests.py --help")
    print("    📖 Mostra esta ajuda")
    print()
    print("=" * 80)
    print("🎯 RECOMENDAÇÃO:")
    print("   Para desenvolvimento local: python run_tests.py --sqlite")
    print("   Para CI/CD ou produção: python run_tests.py --all")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Execute testes do projeto GeoAPI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sqlite", 
        action="store_true", 
        help="Executa apenas testes compatíveis com SQLite (recomendado para desenvolvimento)"
    )
    group.add_argument(
        "--all", 
        action="store_true", 
        help="Executa todos os testes (requer PostgreSQL/PostGIS)"
    )
    group.add_argument(
        "--help-tests", 
        action="store_true", 
        help="Mostra informações detalhadas sobre os testes"
    )
    
    args = parser.parse_args()
    
    if args.help_tests:
        show_help()
        return 0
    
    print("=" * 80)
    print("🔬 GeoAPI - Executor de Testes")
    print("=" * 80)
    
    success = False  # Inicializa a variável
    
    if args.sqlite:
        success = run_sqlite_tests()
        
        print("\n📝 Testes que precisam de PostgreSQL/PostGIS (não executados):")
        postgis_tests = [
            "tests/test_database.py::TestDatabaseFactory::test_get_db_dependency_generator",
            "tests/test_database.py::TestDatabaseFactory::test_get_db_session_direct",
            "tests/test_database.py::TestTableManagement::*",
            "tests/test_database.py::TestDatabaseIntegration::*", 
            "tests/test_models/test_link.py::TestLinkDatabaseOperations::*",
            "tests/test_models/test_speed_record.py::TestSpeedRecordDatabaseOperations::*",
        ]
        for test in postgis_tests:
            print(f"   🔶 {test}")
        
        print("\n💡 Para executar TODOS os testes: python run_tests.py --all")
        
    elif args.all:
        success = run_all_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 Status: SUCESSO!")
        if args.sqlite:
            print("✅ Todos os testes compatíveis com SQLite passaram")
            print("🔧 Projeto pronto para desenvolvimento da API")
        else:
            print("✅ Todos os testes passaram (incluindo PostGIS)")
    else:
        print("⚠️  Status: FALHA")
        if args.all:
            print("🔍 Verifique se PostgreSQL/PostGIS está configurado corretamente")
    
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
