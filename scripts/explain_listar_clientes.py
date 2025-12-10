from pprint import pprint

from config import get_collection


def explain_listar_clientes():
    """
    Roda um find() equivalente ao usado em GET /clientes
    e imprime o plano de execução (queryPlanner.winningPlan).
    """
    bundle = get_collection()
    col = bundle.collection

    try:
        # Filtro bem parecido com o usado na API
        filtro = {
            "marcado_para_exclusao": {"$ne": True},
            "status": "ativo",
            "endereco.estado": "SP",
            "endereco.cidade": "São Paulo",
        }

        cursor = (
            col.find(filtro)
            .sort("nome", 1)
            .limit(20)
        )

        # Pega o plano de execução
        explain = cursor.explain()

        print("\n=== queryPlanner.winningPlan ===")
        winning_plan = explain.get("queryPlanner", {}).get("winningPlan", {})
        pprint(winning_plan)

        # Função auxiliar para tentar achar o nome do índice usado
        def encontrar_index_name(plan: dict):
            if not isinstance(plan, dict):
                return None

            if plan.get("indexName"):
                return plan["indexName"]

            input_stage = plan.get("inputStage")
            if isinstance(input_stage, dict) and input_stage.get("indexName"):
                return input_stage["indexName"]

            # Explora recursivamente subestágios comuns
            for key in ("inputStage", "inputStages", "shards", "children"):
                child = plan.get(key)
                if isinstance(child, dict):
                    found = encontrar_index_name(child)
                    if found:
                        return found
                elif isinstance(child, list):
                    for c in child:
                        found = encontrar_index_name(c)
                        if found:
                            return found
            return None

        index_name = encontrar_index_name(winning_plan)
        print("\n=== Índice identificado ===")
        print(index_name or "(nenhum índice encontrado no plano)")

    finally:
        bundle.client.close()
        print("\n✓ Conexão com MongoDB fechada")


if __name__ == "__main__":
    explain_listar_clientes()
