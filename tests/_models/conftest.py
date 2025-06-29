"""
Este arquivo previne que o pytest colete modelos deste diretório.
"""
import pytest

# Impede que o pytest colete classes deste diretório
collect_ignore = ["simplified_models.py"]
