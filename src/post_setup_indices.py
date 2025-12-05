"""
Script para garantir os índices da coleção de clientes.

Pode ser executado sempre que o ambiente subir:

    python -m src.post_setup_indices
"""

from pymongo import ASCENDING
from pymongo.errors import PyMongoError

from config import get_collection


def ensure_indexes():
    bundle = get_collection()
    col = bundle.collection

    print(f"Conectado a MongoDB em DB={bundle.db.name}, coleção={col.name}")

    try:
        # Índice único em CPF (evita duplicidade de clientes)
        col.create_index(
            [("cpf", ASCENDING)],
            name="cpf_1",
            unique=True,
        )
        print("✓ Índice único em cpf garantido (cpf_1)")

        # Índice para buscas por cidade + nome (relatórios e listagens ordenadas)
        col.create_index(
            [("endereco.cidade", ASCENDING), ("nome", ASCENDING)],
            name="endereco.cidade_1_nome_1",
        )
        print("✓ Índice em endereco.cidade + nome garantido (endereco.cidade_1_nome_1)")

        # Índice para relatórios por UF + cidade
        col.create_index(
            [("endereco.estado", ASCENDING), ("endereco.cidade", ASCENDING)],
            name="estado_cidade_1",
        )
        print("✓ Índice em endereco.estado + endereco.cidade garantido (estado_cidade_1)")

        # Índice composto para status + UF + cidade
        # Útil para relatórios de clientes inativos por cidade/estado direto no MongoDB
        col.create_index(
            [
                ("status", ASCENDING),
                ("endereco.estado", ASCENDING),
                ("endereco.cidade", ASCENDING),
            ],
            name="status_estado_cidade_1",
        )
        print(
            "✓ Índice composto status + endereco.estado + endereco.cidade garantido (status_estado_cidade_1)"
        )


        # Índice para consultas por status (ativos/inativos)
        col.create_index(
            [("status", ASCENDING)],
            name="status_1",
        )
        print("✓ Índice em status garantido (status_1)")

    except PyMongoError as e:
        print(f"✗ Erro ao criar/garantir índices: {e}")
    finally:
        bundle.client.close()
        print("✓ Conexão com MongoDB fechada")


if __name__ == "__main__":
    ensure_indexes()
