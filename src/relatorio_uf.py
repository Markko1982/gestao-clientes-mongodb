from pathlib import Path
import sys
import csv

# Garante que a raiz do projeto esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection


def gerar_relatorio_uf():
    """Relatório de clientes por UF, com ativos x inativos."""
    col = get_collection()

    total_geral = col.count_documents({})

    if total_geral == 0:
        print("✗ Nenhum cliente cadastrado.")
        return

    # Agrupa por UF (campo endereco.estado)
    pipeline = [
        {
            "$group": {
                "_id": "$endereco.estado",
                "total": {"$sum": 1},
                "ativos": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$status", "ativo"]},
                            1,
                            0,
                        ]
                    }
                },
                "inativos": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$status", "inativo"]},
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {"$sort": {"total": -1}},
    ]

    docs = list(col.aggregate(pipeline))

    if not docs:
        print("✗ Nenhum cliente encontrado no agregador.")
        return

    print("\nRELATÓRIO DE CLIENTES POR UF\n")
    print(f"Total de clientes: {total_geral}\n")

    header = f"{'UF':<4} {'Qtde':>8} {'% total':>8} {'Ativos':>8} {'Inativos':>10} {'% ativos':>10}"
    print(header)
    print("-" * len(header))

    linhas_csv = []

    for d in docs:
        uf = d["_id"] or "??"
        total = d["total"]
        ativos = d.get("ativos", 0)
        inativos = d.get("inativos", 0)

        perc_total = (total / total_geral * 100) if total_geral else 0
        perc_ativos = (ativos / total * 100) if total else 0

        print(
            f"{uf:<4} "
            f"{total:>8} "
            f"{perc_total:>7.2f}% "
            f"{ativos:>8} "
            f"{inativos:>10} "
            f"{perc_ativos:>9.2f}%"
        )

        linhas_csv.append([uf, total, perc_total, ativos, inativos, perc_ativos])

    print("-" * len(header))

    # Salva CSV em dados/clientes_por_uf.csv
    dados_dir = ROOT / "dados"
    dados_dir.mkdir(exist_ok=True)
    csv_path = dados_dir / "clientes_por_uf.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["UF", "total", "perc_total", "ativos", "inativos", "perc_ativos"])
        for linha in linhas_csv:
            writer.writerow(linha)

    print(f"\nArquivo CSV gerado em: {csv_path}")
    print("Use o CSV para análises mais detalhadas por UF.")


if __name__ == "__main__":
    gerar_relatorio_uf()
