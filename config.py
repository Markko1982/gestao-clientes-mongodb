from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


# Diretório raiz do projeto (onde está este config.py e o .env)
ROOT = Path(__file__).resolve().parent
env_path = ROOT / ".env"

# Carrega variáveis do .env, se existir
if env_path.exists():
    load_dotenv(env_path)


def _get_env(name: str, *, default: str | None = None, required: bool = False) -> str:
    """Lê variável de ambiente, com opção de marcar como obrigatória."""
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(
            f"Variável de ambiente {name} não definida. "
            f"Defina {name} no arquivo .env ou no ambiente antes de rodar a aplicação."
        )
    return value


# URL de conexão com o MongoDB (OBRIGATÓRIA, sem hardcode)
MONGO_URI: str = _get_env("MONGO_URI", required=True)

# Nome do banco e da coleção padrão (podem ter default razoável)
MONGO_DB_NAME: str = _get_env("MONGO_DB_NAME", default="empresa_db")
MONGO_COLLECTION_CLIENTES: str = _get_env("MONGO_COLLECTION_CLIENTES", default="clientes")

# Alias para compatibilidade com código antigo
MONGO_COLLECTION_NAME: str = MONGO_COLLECTION_CLIENTES


@dataclass
class _CollectionBundle:
    """Pacote com client, db e collection principal de clientes."""

    client: MongoClient
    db: Database
    collection: Collection

    def __iter__(self):
        """Permite: client, db, col = get_collection()"""
        yield self.client
        yield self.db
        yield self.collection

    def __repr__(self) -> str:  # pragma: no cover - só para debug
        return f"<CollectionBundle db={self.db.name!r} collection={self.collection.name!r}>"


def get_collection() -> _CollectionBundle:
    """Retorna client, db e coleção principal de clientes.

    Exemplos de uso:

        bundle = get_collection()
        col = bundle.collection

        client, db, col = get_collection()
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_CLIENTES]
    return _CollectionBundle(client=client, db=db, collection=collection)
