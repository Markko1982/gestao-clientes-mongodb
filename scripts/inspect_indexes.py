"""
Mostra os índices atuais da coleção 'clientes'.
"""

from pprint import pprint
from config import get_collection


def main():
    bundle = get_collection()
    col = bundle.collection

    try:
        print(f"DB  : {bundle.db.name}")
        print(f"Coll: {col.name}\n")

        print("Índices existentes (col.index_information()):\n")
        info = col.index_information()
        pprint(info)
    finally:
        bundle.client.close()
        print("\n✓ Conexão com MongoDB fechada")


if __name__ == "__main__":
    main()
