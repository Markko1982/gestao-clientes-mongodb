"""
Lista CPFs que ficariam duplicados depois da normalização
(removendo pontos e traço).

⚠ Este script NÃO altera nada no banco.
"""

import re
from pprint import pprint
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
                "status": doc.get("status"),
            }
            mapa.setdefault(cpf_norm, []).append(info)

        duplicados = {k: v for k, v in mapa.items() if len(v) > 1}

        print("===== RESUMO =====")
        print(f"Total de documentos analisados (cpf string): {total_analisados}")
        print(f"Total de CPFs normalizados distintos: {len(mapa)}")
        print(f"Total de CPFs com duplicidade: {len(duplicados)}\n")

        if duplicados:
            print("Alguns CPFs normalizados com duplicidade (máx. 20):\n")
            mostrados = 0
            for cpf_norm, docs in duplicados.items():
                print(f"CPF normalizado: {cpf_norm}  | qtd documentos: {len(docs)}")
                for d in docs[:5]:
                    pprint(d)
                print("-" * 60)

                mostrados += 1
                if mostrados >= 20:
                    break

        print("\n✅ Análise concluída. Nenhuma alteração foi feita no banco.")
    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
