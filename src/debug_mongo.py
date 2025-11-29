"""
Script de debug para visualizar o uso de índices com explain().

Uso:
    python -m src.debug_mongo
"""

from pprint import pprint

from config import get_collection


def show_explain(label: str, cursor):
    """
    Executa explain() em um cursor e mostra o plano vencedor.
    """
    print("\n" + "=" * 80)
    print(label)
    print("-" * 80)
    plan = cursor.explain()

    query_planner = plan.get("queryPlanner") or {}
    winning_plan = query_planner.get("winningPlan")

    if winning_plan:
        pprint(winning_plan)
    else:
        # Se a estrutura for diferente, mostra tudo
        pprint(plan)


def main():
    bundle = get_collection()
    col = bundle.collection
    print(f"Conectado em DB={bundle.db.name}, coleção={col.name}")

    # 1) Busca por CPF - deve usar índice cpf_1
    show_explain(
        "1) Busca por CPF (esperado usar índice cpf_1)",
        col.find({"cpf": "00000000000"}),
    )

    # 2) Busca por cidade + ordenação por nome - deve usar endereco.cidade_1_nome_1
    show_explain(
        "2) Busca por cidade, ordenando por nome (esperado usar endereco.cidade_1_nome_1)",
        col.find({"endereco.cidade": "São Paulo"}).sort("nome", 1),
    )

    # 3) Busca por UF + cidade - deve usar estado_cidade_1
    show_explain(
        "3) Busca por UF + cidade (esperado usar estado_cidade_1)",
        col.find({"endereco.estado": "SP", "endereco.cidade": "São Paulo"}),
    )

    # 4) Busca por status - deve usar status_1
    show_explain(
        "4) Busca por status=inativo (esperado usar status_1)",
        col.find({"status": "inativo"}),
    )

    bundle.client.close()
    print("\n✓ Conexão com MongoDB fechada")


if __name__ == "__main__":
    main()
