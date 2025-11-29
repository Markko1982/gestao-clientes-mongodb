from __future__ import annotations

from collections import Counter
from pathlib import Path
from datetime import datetime
import csv

from config import get_collection


ROOT = Path(__file__).resolve().parent.parent
DADOS_DIR = ROOT / "dados"


def calcular_idade(data_nascimento_str: str) -> int:
    """Calcula idade a partir da data de nascimento no formato YYYY-MM-DD."""
    try:
        dt = datetime.strptime(data_nascimento_str, "%Y-%m-%d")
    except Exception:
        return 0

    hoje = datetime.now()
    idade = hoje.year - dt.year
    if (hoje.month, hoje.day) < (dt.month, dt.day):
        idade -= 1
    return max(0, idade)


def classificar_faixa_etaria(idade: int) -> str:
    """Classifica idade em faixas etárias amigáveis."""
    if idade < 18:
        return "0-17"
    if idade <= 24:
        return "18-24"
    if idade <= 34:
        return "25-34"
    if idade <= 44:
        return "35-44"
    if idade <= 54:
        return "45-54"
    if idade <= 64:
        return "55-64"
    if idade <= 79:
        return "65-79"
    return "80+"


def gerar_dashboard_executivo() -> None:
    """Gera um resumo executivo com métricas principais dos clientes."""
    bundle = get_collection()
    col = bundle.collection
    DADOS_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 80)
    print("DASHBOARD EXECUTIVO - CLIENTES")
    print("=" * 80)

    # --- Visão geral: totais / status ---
    total_clientes = col.count_documents({})
    total_ativos = col.count_documents({"status": "ativo"})
    total_inativos = col.count_documents({"status": "inativo"})
    outros_status = total_clientes - total_ativos - total_inativos

    perc_ativos = (total_ativos / total_clientes * 100) if total_clientes else 0.0
    perc_inativos = (total_inativos / total_clientes * 100) if total_clientes else 0.0

    print("\nRESUMO GERAL")
    print("-" * 80)
    print(f"Total de clientes : {total_clientes:8d}")
    print(f"Ativos            : {total_ativos:8d}  ({perc_ativos:5.2f} %)")
    print(f"Inativos          : {total_inativos:8d}  ({perc_inativos:5.2f} %)")
    print(f"Outros status     : {outros_status:8d}")
    print("-" * 80)

    # --- Top 10 UFs por quantidade de clientes ---
    pipeline_uf = [
        {"$group": {"_id": "$endereco.estado", "qtde": {"$sum": 1}}},
        {"$sort": {"qtde": -1}},
        {"$limit": 10},
    ]
    resultados_uf = list(col.aggregate(pipeline_uf))

    print("\nTOP 10 UFs POR QUANTIDADE DE CLIENTES")
    print("-" * 80)
    print(f"{'UF':<4} {'Qtde':>8}   {'% do total':>12}")
    print("-" * 80)
    linhas_csv_uf: list[list[str | int | float]] = []
    for r in resultados_uf:
        uf = r["_id"] or "??"
        qtde = r["qtde"]
        perc = (qtde / total_clientes * 100) if total_clientes else 0.0
        print(f"{uf:<4} {qtde:8d}   {perc:11.2f}%")
        linhas_csv_uf.append([uf, qtde, f"{perc:.2f}"])

    # --- Top 10 cidades (cidade + UF) ---
    pipeline_cidade = [
        {
            "$group": {
                "_id": {"cidade": "$endereco.cidade", "uf": "$endereco.estado"},
                "qtde": {"$sum": 1},
            }
        },
        {"$sort": {"qtde": -1, "_id.uf": 1, "_id.cidade": 1}},
        {"$limit": 10},
    ]
    resultados_cidade = list(col.aggregate(pipeline_cidade))

    print("\nTOP 10 CIDADES (TODAS AS UFs)")
    print("-" * 80)
    print(f"{'Cidade / UF':<40} {'Qtde':>8}   {'% do total':>12}")
    print("-" * 80)
    linhas_csv_cidade: list[list[str | int | float]] = []
    for r in resultados_cidade:
        cidade = r["_id"]["cidade"] or "??"
        uf = r["_id"]["uf"] or "??"
        qtde = r["qtde"]
        perc = (qtde / total_clientes * 100) if total_clientes else 0.0
        label = f"{cidade} - {uf}"
        print(f"{label:<40} {qtde:8d}   {perc:11.2f}%")
        linhas_csv_cidade.append([cidade, uf, qtde, f"{perc:.2f}"])

    # --- Distribuição por faixa etária (em Python) ---
    print("\nDISTRIBUIÇÃO POR FAIXA ETÁRIA (aprox.)")
    print("-" * 80)

    faixas = Counter()
    # Projeção mínima para evitar trafegar documento inteiro
    cursor = col.find(
        {},
        {"_id": 0, "data_nascimento": 1},
    )
    for doc in cursor:
        idade = calcular_idade(doc.get("data_nascimento", ""))
        faixa = classificar_faixa_etaria(idade)
        faixas[faixa] += 1

    # Ordem das faixas
    ordem_faixas = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65-79", "80+"]
    linhas_csv_faixas: list[list[str | int | float]] = []

    print(f"{'Faixa etária':<12} {'Qtde':>8}   {'% do total':>12}")
    print("-" * 80)
    for faixa in ordem_faixas:
        qtde = faixas.get(faixa, 0)
        perc = (qtde / total_clientes * 100) if total_clientes else 0.0
        print(f"{faixa:<12} {qtde:8d}   {perc:11.2f}%")
        linhas_csv_faixas.append([faixa, qtde, f"{perc:.2f}"])

    # --- Exportar CSVs resumidos ---
    csv_uf = DADOS_DIR / "dashboard_top_ufs.csv"
    csv_cidades = DADOS_DIR / "dashboard_top_cidades.csv"
    csv_faixas = DADOS_DIR / "dashboard_faixa_etaria.csv"

    with csv_uf.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["uf", "qtde", "perc_total"])
        w.writerows(linhas_csv_uf)

    with csv_cidades.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["cidade", "uf", "qtde", "perc_total"])
        w.writerows(linhas_csv_cidade)

    with csv_faixas.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["faixa_etaria", "qtde", "perc_total"])
        w.writerows(linhas_csv_faixas)

    print("\nArquivos CSV gerados:")
    print(f"- {csv_uf}")
    print(f"- {csv_cidades}")
    print(f"- {csv_faixas}")

    print("\n" + "=" * 80)
    print("✓ DASHBOARD EXECUTIVO GERADO COM SUCESSO")
    print("=" * 80)

    bundle.client.close()
    print("✓ Conexão com MongoDB fechada")


if __name__ == "__main__":
    gerar_dashboard_executivo()
