"""
Exporta para CSV todos os CPFs que ficam duplicados após a normalização
(removendo pontos e traços).

⚠ Este script NÃO altera nada no banco.
Gera um arquivo em backups/cpfs_duplicados_YYYYMMDD_HHMMSS.csv
"""

import os
import re
import csv
from datetime import datetime
from config import get_collection


def normalizar_cpf(cpf_str):
    if not isinstance(cpf_str, str):
        return None
    apenas_digitos = re.sub(r"\D", "", cpf_str or "")
    if len(apenas_digitos) != 11:
        return None
    return apenas_digitos


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    try:
        print(f"Analisando coleção {col.name!r} (db={col.database.name!r})...\n")

        mapa = {}
        total_analisados = 0

        for doc in col.find({"cpf": {"$type": "string"}}):
            total_analisados += 1
            cpf_original = doc.get("cpf")
            cpf_norm = normalizar_cpf(cpf_original)
            if not cpf_norm:
                continue

            info = {
                "_id": str(doc.get("_id")),
                "cpf_original": cpf_original,
                "nome": doc.get("nome"),
                "email": doc.get("email"),
                "status": doc.get("status"),
            }
            mapa.setdefault(cpf_norm, []).append(info)

        duplicados = {k: v for k, v in mapa.items() if len(v) > 1}

        print("===== RESUMO =====")
        print(f"Total de documentos analisados (cpf string): {total_analisados}")
        print(f"Total de CPFs normalizados distintos: {len(mapa)}")
        print(f"Total de CPFs com duplicidade: {len(duplicados)}")

        if not duplicados:
            print("\nNenhum CPF duplicado encontrado. Nada para exportar.")
            return

        os.makedirs("backups", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"backups/cpfs_duplicados_{timestamp}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                ["cpf_normalizado", "doc_id", "cpf_original", "nome", "email", "status"]
            )

            for cpf_norm, docs in duplicados.items():
                for d in docs:
                    writer.writerow(
                        [
                            cpf_norm,
                            d["_id"],
                            d.get("cpf_original"),
                            d.get("nome"),
                            d.get("email"),
                            d.get("status"),
                        ]
                    )

        print(f"\n✅ Exportação concluída.")
        print(f"Arquivo gerado em: {filename}")
        print("Abra esse CSV em uma planilha para analisar os casos manualmente.")
    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
