from pathlib import Path
import sys
import csv

# Garante que o diretório raiz (onde está config.py) esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection  # type: ignore


def gerar_relatorio_cidades():
    """Gera relatório de clientes por cidade (interativo)."""
    col = get_collection()

    print("RELATÓRIO DE CLIENTES POR CIDADE\n")

    uf_input = input("Filtrar por UF (ex: SP). Deixe em branco para todos os estados: ").strip()
    uf_filtro = uf_input.upper()

    limite_str = input("Quantas cidades exibir no terminal? (ex: 10, 50, 0 = todas) [50]: ").strip() or "50"
    try:
        limite = int(limite_str)
    except ValueError:
        print("\nValor inválido. Usando limite padrão (50).")
        limite = 50

    # ----- Monta filtro (match) -----
    match = {}
    if uf_filtro:
        match["endereco.estado"] = uf_filtro  # campo correto do documento

    # ----- Pipeline para o que vai aparecer no terminal (TOP N) -----
    pipeline = []
    if match:
        pipeline.append({"$match": match})

    pipeline.extend(
        [
            {
                "$group": {
                    "_id": {"cidade": "$endereco.cidade", "uf": "$endereco.estado"},
                    "qtde": {"$sum": 1},
                }
            },
            {"$sort": {"qtde": -1}},
        ]
    )

    if limite > 0:
        pipeline.append({"$limit": limite})

    resultados = list(col.aggregate(pipeline))

    # Total dentro do filtro (para %)
    total_filtrado = col.count_documents(match if match else {})

    if not resultados or total_filtrado == 0:
        print("\n✗ Nenhum cliente encontrado para esse filtro.")
        return

    # ----- Impressão no terminal -----
    if uf_filtro:
        print(f"\n(Exibindo TOP {limite if limite > 0 else 'todas'} cidades da UF {uf_filtro})")
        print(f"Total de clientes na UF {uf_filtro}: {total_filtrado}\n")
    else:
        print(f"\n(Exibindo TOP {limite if limite > 0 else 'todas'} cidades de todos os estados)")
        print(f"Total de clientes: {total_filtrado}\n")

    cabecalho = f"{'Cidade / UF':40} | {'Qtde':>7} | {'% do total':>10}"
    print(cabecalho)
    print("-" * len(cabecalho))

    for r in resultados:
        cidade = r["_id"]["cidade"]
        uf = r["_id"]["uf"]
        qtde = r["qtde"]
        perc = (qtde / total_filtrado * 100) if total_filtrado else 0.0

        nome_cidade = f"{cidade} - {uf}"
        qtde_str = f"{qtde:,}".replace(",", ".")
        perc_str = f"{perc:5.2f}%"

        print(f"{nome_cidade:40} | {qtde_str:>7} | {perc_str:>10}")

    # ----- Geração do CSV com a LISTA COMPLETA de cidades -----
    pipeline_csv = []
    if match:
        pipeline_csv.append({"$match": match})

    pipeline_csv.extend(
        [
            {
                "$group": {
                    "_id": {"cidade": "$endereco.cidade", "uf": "$endereco.estado"},
                    "qtde": {"$sum": 1},
                }
            },
            {"$sort": {"qtde": -1}},
        ]
    )

    todos_resultados = list(col.aggregate(pipeline_csv))

    dados_dir = ROOT / "dados"
    dados_dir.mkdir(exist_ok=True)

    csv_path = dados_dir / "clientes_por_cidade.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["cidade", "uf", "qtde", "percentual"])
        for r in todos_resultados:
            cidade = r["_id"]["cidade"]
            uf = r["_id"]["uf"]
            qtde = r["qtde"]
            perc = (qtde / total_filtrado * 100) if total_filtrado else 0.0
            writer.writerow([cidade, uf, qtde, f"{perc:.2f}"])

    print(f"\nArquivo CSV gerado em: {csv_path}")
    print("Use o CSV para analisar a lista COMPLETA de cidades.\n")


if __name__ == "__main__":
    gerar_relatorio_cidades()
