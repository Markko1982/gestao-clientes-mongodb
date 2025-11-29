"""
Mostra um resumo dos documentos marcados para exclusão:

- Conta quantos possuem marcado_para_exclusao = true
- Lista alguns exemplos com campos principais
"""

from pprint import pprint
from config import get_collection


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    try:
        print(f"Coleção: {col.name!r} (db={col.database.name!r})\n")

        filtro = {"marcado_para_exclusao": True}

        total = col.count_documents(filtro)
        print(f"Total de documentos marcados_para_exclusao = true: {total}\n")

        print("Alguns exemplos (até 10):")
        for doc in col.find(
            filtro,
            {
                "nome": 1,
                "cpf": 1,
                "status": 1,
                "cpf_principal_id": 1,
            },
        ).limit(10):
            pprint(
                {
                    "_id": str(doc.get("_id")),
                    "nome": doc.get("nome"),
                    "cpf": doc.get("cpf"),
                    "status": doc.get("status"),
                    "cpf_principal_id": str(doc.get("cpf_principal_id"))
                    if doc.get("cpf_principal_id")
                    else None,
                }
            )
            print("-" * 60)

        print("\n✅ Inspeção concluída. Nenhuma alteração foi feita no banco.")
    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
