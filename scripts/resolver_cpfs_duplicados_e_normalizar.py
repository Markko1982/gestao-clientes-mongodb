"""
Resolve os CPFs duplicados após a normalização e
ajusta o CPF do documento principal para 11 dígitos.

Regra pensada para o cenário atual:

- Para cada CPF normalizado que aparece em 2+ documentos:
    - escolhe 1 documento principal (preferindo status "ativo");
    - remove fisicamente os documentos secundários;
    - atualiza o CPF do principal para o formato normalizado (11 dígitos),
      se ainda estiver com pontos/traço.

⚠ ESTE SCRIPT ALTERA DOCUMENTOS NA COLEÇÃO 'clientes'.

Recomendações ANTES de rodar:
- Ter backup da coleção (você já tem export e backups).
- Já ter rodado:
    - python -m scripts.listar_cpfs_duplicados_normalizados
    - python -m scripts.export_cpfs_duplicados_normalizados_csv
"""

import re
from pprint import pprint
from config import get_collection


def normalizar_cpf(cpf_str: str) -> str:
    if not isinstance(cpf_str, str):
        return ""
    return re.sub(r"\D", "", cpf_str)


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    try:
        print("Analisando coleção 'clientes' para CPFs duplicados...\n")

        cursor = col.find(
            {"cpf": {"$type": "string"}},
            {"cpf": 1, "status": 1},
        )

        mapa = {}
        total_analisados = 0

        for doc in cursor:
            total_analisados += 1
            cpf_str = doc.get("cpf")
            cpf_norm = normalizar_cpf(cpf_str)
            if len(cpf_norm) != 11:
                # Ignora CPFs que não viram 11 dígitos
                continue

            mapa.setdefault(cpf_norm, []).append(doc)

        # Filtra apenas CPFs com mais de 1 documento
        duplicados = {cpf: docs for cpf, docs in mapa.items() if len(docs) > 1}

        print("===== RESUMO INICIAL =====")
        print(f"Total analisados (cpf string): {total_analisados}")
        print(f"Total CPFs normalizados distintos: {len(mapa)}")
        print(f"Total CPFs com duplicidade: {len(duplicados)}\n")

        if not duplicados:
            print("Nenhum CPF duplicado encontrado. Nada a fazer.")
            return

        exemplos = []
        removidos_total = 0
        atualizados_total = 0

        for cpf_norm, docs in duplicados.items():
            # Escolhe o principal: prioriza 'ativo'
            principais = [d for d in docs if d.get("status") == "ativo"]
            if principais:
                principal = principais[0]
            else:
                principal = docs[0]

            secundarios = [d for d in docs if d["_id"] != principal["_id"]]

            # Guarda exemplo para log
            exemplos.append(
                {
                    "cpf_normalizado": cpf_norm,
                    "principal": {
                        "_id": str(principal["_id"]),
                        "cpf": principal.get("cpf"),
                        "status": principal.get("status"),
                    },
                    "secundarios": [
                        {
                            "_id": str(d["_id"]),
                            "cpf": d.get("cpf"),
                            "status": d.get("status"),
                        }
                        for d in secundarios
                    ],
                }
            )

            # 1) Remove documentos secundários
            if secundarios:
                resultado_del = col.delete_many(
                    {"_id": {"$in": [d["_id"] for d in secundarios]}}
                )
                removidos_total += resultado_del.deleted_count

            # 2) Atualiza CPF do principal para o normalizado, se precisar
            cpf_principal_atual = principal.get("cpf")
            if cpf_principal_atual != cpf_norm:
                res_up = col.update_one(
                    {"_id": principal["_id"]},
                    {"$set": {"cpf": cpf_norm}},
                )
                if res_up.modified_count == 1:
                    atualizados_total += 1

        print("\n===== RESUMO FINAL =====")
        print(f"Total de CPFs com duplicidade tratados: {len(duplicados)}")
        print(f"Documentos secundários removidos: {removidos_total}")
        print(f"Documentos principais com CPF atualizado: {atualizados_total}\n")

        if exemplos:
            print("Alguns exemplos de grupos tratados (principal x secundários):")
            for ex in exemplos[:10]:
                pprint(ex)
                print("-" * 60)

        print("✅ Tratamento de duplicados concluído.")

    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
