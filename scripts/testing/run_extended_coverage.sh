#!/bin/bash
# Script para executar todos os testes de cobertura adicionados

echo "Executando testes de cobertura adicionais..."

# Limpando cache do Python
echo "Limpando cache do Python..."
find . -type d -name '__pycache__' -exec rm -rf {} +
find . -type f -name '*.pyc' -delete
rm -rf .pytest_cache .mypy_cache .pylint.d

# Executando todos os testes com cobertura
echo "Executando testes com cobertura para database.py..."
python -m pytest tests/test_database.py tests/test_database_additional.py tests/test_database_postgis.py -v --cov=app.core.database

echo "Executando testes com cobertura para logging.py..."
python -m pytest tests/test_logging.py tests/test_logging_additional.py tests/test_logging_extended.py -v --cov=app.core.logging

echo "Executando testes com cobertura para os modelos..."
python -m pytest tests/test_models/test_link.py tests/test_models/test_link_extended.py -v --cov=app.models.link
python -m pytest tests/test_models/test_speed_record.py tests/test_models/test_speed_record_extended.py tests/test_models/test_speed_record_additional.py -v --cov=app.models.speed_record

# Gerando relatório completo de cobertura
echo "Gerando relatório completo de cobertura..."
python -m pytest tests/test_database.py tests/test_database_additional.py tests/test_database_postgis.py tests/test_logging.py tests/test_logging_additional.py tests/test_logging_extended.py tests/test_models/test_link.py tests/test_models/test_link_extended.py tests/test_models/test_speed_record.py tests/test_models/test_speed_record_extended.py tests/test_models/test_speed_record_additional.py -v --cov=app.core --cov=app.models --cov-report=html

echo "Testes completos. Verifique o relatório de cobertura em htmlcov/index.html"
