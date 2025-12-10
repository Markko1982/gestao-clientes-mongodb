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

    try:
        # Índice único em CPF (garante unicidade dos clientes)
        col.create_index(
            [("cpf", ASCENDING)],
            name="cpf_1",
            unique=True,
        )
        print("✓ Índice único em cpf garantido (cpf_1)")

        # Índice simples em status (para filtros gerais)
        col.create_index(
            [("status", ASCENDING)],
            name="status_1",
        )
        print("✓ Índice em status garantido (status_1)")

        # Índice para buscas por cidade ordenando por nome
        col.create_index(
            [
                ("endereco.cidade", ASCENDING),
                ("nome", ASCENDING),
            ],
            name="cidade_nome_1",
        )
        print("✓ Índice em endereco.cidade + nome garantido (cidade_nome_1)")

        # Índice para combinações de estado + cidade
        col.create_index(
            [
                ("endereco.estado", ASCENDING),
                ("endereco.cidade", ASCENDING),
            ],
            name="estado_cidade_1",
        )
        print("✓ Índice em endereco.estado + endereco.cidade garantido (estado_cidade_1)")

        # Índice composto pensado para o endpoint GET /clientes
        # Filtro típico: status, estado, cidade
        # Ordenação: nome ASC
        col.create_index(
            [
                ("status", ASCENDING),
                ("endereco.estado", ASCENDING),
                ("endereco.cidade", ASCENDING),
                ("nome", ASCENDING),
            ],
            name="status_estado_cidade_nome_1",
        )
        print("✓ Índice composto para listagem garantido (status_estado_cidade_nome_1)")

    except PyMongoError as e:
        print(f"✗ Erro ao criar/garantir índices: {e}")
    finally:
        bundle.client.close()
        print("✓ Conexão com MongoDB fechada")


if __name__ == "__main__":
    ensure_indexes()
