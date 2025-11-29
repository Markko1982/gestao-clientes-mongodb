"""
Exporta todos os documentos da coleção 'clientes' para um arquivo JSONL.

- NÃO altera nada no banco.
- Cria um arquivo em backups/clientes_backup_YYYYMMDD_HHMMSS.jsonl
- Cada linha do arquivo é um documento JSON (formato compatível com bson.json_util).
"""

import os
from datetime import datetime
from bson.json_util import dumps
from config import get_collection


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"backups/clientes_backup_{timestamp}.jsonl"

    total = 0
    print(f"Exportando documentos da coleção {col.name!r} (db={col.database.name!r})...")
    print(f"Arquivo de saída: {filename}")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            for doc in col.find({}):
                f.write(dumps(doc))
                f.write("\n")
                total += 1

        print(f"\n✅ Exportação concluída.")
        print(f"Total de documentos exportados: {total}")
        print(f"Arquivo gerado em: {filename}")
    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
