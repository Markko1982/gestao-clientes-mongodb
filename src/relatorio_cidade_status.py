from pathlib import Path
import sys
import csv

# Garante que o diretório raiz esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from config import get_collection


def gerar_relatorio_cidade_status():
    col = get_collection()

    print("RELATÓRIO DE CLIENTES POR CIDADE (ATIVOS x INATIVOS)\n")

    uf_filtro = input(
        "Filtrar por UF (ex: SP). Deixe em branco para todos os estados: "
    ).strip().lower()

    limite_str = input(
        "Quantas cidades exibir? (10, 20, 50, 0 = todas) [20]: "
    ).strip() or "20"

    try:
        limite = int(limite_str)
        if limite < 0:
            raise ValueError
    except ValueError:
        print("\nValor inválido. Usando limite padrão (20).")
        limite = 20

    # 1) Agrega todas as cidades no Mongo (sem filtrar UF aqui)
    pipeline = [
        {
            "$group": {
                "_id": {
                    "cidade": "$endereco.cidade",
                    "uf": "$endereco.estado",
                },
                "total": {"$sum": 1},
                "ativos": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "ativo"]}, 1, 0]
                    }
                },
                "inativos": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "inativo"]}, 1, 0]
                    }
                },
            }
        },
        {
            "$sort": {
                "total": -1,
                "_id.uf": 1,
                "_id.cidade": 1,
            }
        },
    ]

    docs = list(col.aggregate(pipeline))

    if not docs:
        print("\n✗ Nenhum cliente encontrado (coleção vazia?).")
        return

    # 2) Filtro por UF em Python (case-insensitive)
    if uf_filtro:
        docs = [
            d
            for d in docs
            if (d["_id"]["uf"] or "").lower() == uf_filtro
        ]

        if not docs:
            print("\n✗ Nenhum cliente encontrado para esse filtro.")
            return

    total_geral = sum(d["total"] for d in docs)

    # Aplica limite apenas para exibição (não para o CSV)
    if limite > 0:
        exibidos = docs[:limite]
    else:
        exibidos = docs

    print(f"\nTotal de clientes: {total_geral}\n")
    print(
        "Cidade / UF".ljust(35),
        "|",
        "Total".rjust(6),
        "|",
        "% do total".rjust(10),
        "|",
        "Ativos".rjust(7),
        "|",
        "% ativos".rjust(10),
        "|",
        "Inativos".rjust(9),
        "|",
        "% inat.".rjust(9),
    )
    print("-" * 90)

    for d in exibidos:
        cidade = d["_id"]["cidade"] or "(sem cidade)"
        uf = (d["_id"]["uf"] or "").upper()
        total = d["total"]
        ativos = d["ativos"]
        inativos = d["inativos"]

        perc_total = (total / total_geral * 100) if total_geral else 0
        perc_ativos = (ativos / total * 100) if total else 0
        perc_inativos = (inativos / total * 100) if total else 0

        label = f"{cidade} - {uf}".ljust(35)
        print(
            label,
            "|",
            f"{total:6d}",
            "|",
            f"{perc_total:9.2f}%",
            "|",
            f"{ativos:7d}",
            "|",
            f"{perc_ativos:9.2f}%",
            "|",
            f"{inativos:9d}",
            "|",
            f"{perc_inativos:8.2f}%",
        )

    # 3) Gera CSV completo (todas as cidades do filtro, não só as exibidas)
    dados_dir = ROOT / "dados"
    dados_dir.mkdir(exist_ok=True)
    csv_path = dados_dir / "clientes_por_cidade_status.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "uf",
                "cidade",
                "total",
                "ativos",
                "inativos",
                "perc_total",
                "perc_ativos",
                "perc_inativos",
            ]
        )
        for d in docs:
            cidade = d["_id"]["cidade"] or ""
            uf = (d["_id"]["uf"] or "").upper()
            total = d["total"]
            ativos = d["ativos"]
            inativos = d["inativos"]

            perc_total = (total / total_geral * 100) if total_geral else 0
            perc_ativos = (ativos / total * 100) if total else 0
            perc_inativos = (inativos / total * 100) if total else 0

            writer.writerow(
                [
                    uf,
                    cidade,
                    total,
                    ativos,
                    inativos,
                    f"{perc_total:.4f}",
                    f"{perc_ativos:.4f}",
                    f"{perc_inativos:.4f}",
                ]
            )

    print(
        f"\nArquivo CSV gerado em: {csv_path}\n"
        "Use o CSV para análises mais detalhadas por cidade."
    )


if __name__ == "__main__":
    gerar_relatorio_cidade_status()
