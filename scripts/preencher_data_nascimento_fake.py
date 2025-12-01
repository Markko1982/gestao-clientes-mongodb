"""
Script para preencher data_nascimento fake para clientes sem esse campo.

- Gera datas entre 18 e 80 anos de idade.
- Primeiro roda em modo DRY RUN (APLICAR_ALTERACOES = False).
- Depois, se você estiver confortável, mude para True para aplicar no banco.
"""

from datetime import date, timedelta
import random

from pymongo import UpdateOne

from config import get_collection


APLICAR_ALTERACOES = True  # mude para True depois de revisar o dry run


def gerar_data_nascimento() -> str:
    """
    Gera uma data de nascimento aleatória (YYYY-MM-DD) com distribuição mais realista.

    Estratégia:
    - 18–25 anos:  15%  (jovens)
    - 26–35 anos:  30%  (adultos início de carreira)
    - 36–50 anos:  30%  (adultos maduros)
    - 51–65 anos:  20%  (meia-idade)
    - 66–80 anos:   5%  (idosos)
    """
    hoje = date.today()

    # Faixas de idade (mínimo, máximo) e pesos associados
    faixas = [
        (18, 25),  # 0
        (26, 35),  # 1
        (36, 50),  # 2
        (51, 65),  # 3
        (66, 80),  # 4
    ]
    pesos = [0.15, 0.30, 0.30, 0.20, 0.05]

    # Escolhe uma faixa de idade de acordo com os pesos
    faixa_escolhida = random.choices(faixas, weights=pesos, k=1)[0]
    idade_min, idade_max = faixa_escolhida

    # Dentro da faixa, escolhe uma idade uniforme
    idade = random.randint(idade_min, idade_max)

    # Converte idade em "dias atrás"
    delta_dias = idade * 365
    data = hoje - timedelta(days=delta_dias)
    return data.strftime("%Y-%m-%d")




def main() -> None:
    bundle = get_collection()
    col = bundle.collection

    print("Analisando clientes sem data_nascimento definida...")

    filtro = {
    "marcado_para_exclusao": {"$ne": True},
}


    projecao = {"_id": 1, "cpf": 1, "nome": 1}

    cursor = col.find(filtro, projecao)

    total_alvo = 0
    exemplos = []
    operacoes = []

    for doc in cursor:
        total_alvo += 1
        nova_data = gerar_data_nascimento()

        if len(exemplos) < 5:
            exemplos.append(
                {
                    "_id": str(doc["_id"]),
                    "cpf": doc.get("cpf"),
                    "nome": doc.get("nome"),
                    "data_nascimento_nova": nova_data,
                }
            )

        if APLICAR_ALTERACOES:
            operacoes.append(
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": {"data_nascimento": nova_data}},
                )
            )

    print("\n===== RESUMO DA ANÁLISE =====")
    print(f"Total de clientes sem data_nascimento: {total_alvo}")

    if exemplos:
        print("\nAlguns exemplos de clientes que receberiam data_nascimento:")
        for ex in exemplos:
            print(ex)

    if not APLICAR_ALTERACOES:
        print(
            "\n⚠ Modo DRY RUN: nenhuma alteração foi feita no banco.\n"
            "   Revise os exemplos acima. Se estiver confortável, mude APLICAR_ALTERACOES = True\n"
            "   no arquivo scripts/preencher_data_nascimento_fake.py e rode novamente."
        )
    else:
        print("\nAplicando alterações no banco (bulk_write)...")
        if operacoes:
            resultado = col.bulk_write(operacoes)
            print(f"✅ Documentos atualizados: {resultado.modified_count}")
        else:
            print("Nenhuma operação de update foi gerada.")

    bundle.client.close()
    print("\nConexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
