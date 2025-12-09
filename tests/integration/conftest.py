
# tests/integration/conftest.py
import os
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


# Garante que a RAIZ do projeto (onde está config.py) esteja no PYTHONPATH
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


TEST_DB_NAME = "empresa_db_test"


@pytest.fixture(scope="session")
def app():
    """
    Cria a aplicação FastAPI usando um banco de TESTE.

    - Define MONGO_DB_NAME antes de importar src.api
    - Importa a app só depois de o ambiente estar preparado
    """
    # Garante que vamos usar o banco de teste
    os.environ["MONGO_DB_NAME"] = TEST_DB_NAME

    # Opcional: se quiser, force o URI aqui também (senão pega do .env)
    # os.environ["MONGO_URI"] = "mongodb://admin:admin123@localhost:27017/"

    from src.api import app as fastapi_app

    return fastapi_app


@pytest.fixture(scope="session")
def mongo_collection():
    """
    Retorna a coleção de clientes apontando para o banco de TESTE.
    """
    os.environ["MONGO_DB_NAME"] = TEST_DB_NAME

    from config import get_collection

    bundle = get_collection()
    return bundle.collection


@pytest.fixture
def client(app, mongo_collection):
    """
    Devolve um TestClient para chamar os endpoints da API.

    Depende de:
      - app: a instância FastAPI configurada para o banco de teste
      - mongo_collection: garante que a conexão esteja OK
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def limpar_colecao(mongo_collection):
    """
    Limpa a coleção de clientes antes e depois de CADA teste de integração.

    Isso garante isolamento entre testes.
    """
    # Antes do teste
    mongo_collection.delete_many({})

    yield

    # Depois do teste
    mongo_collection.delete_many({})
