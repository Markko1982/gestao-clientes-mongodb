"""
Análises avançadas de clientes usando Pandas em cima do MongoDB.

Este script reaproveita a função carregar_clientes_dataframe() do
scripts.analise_clientes_pandas e produz:

- Visão geral de distribuição de status (contagem e %).
- Tabela de status por estado (UF), com % de inativos.
- Top 10 estados com maior % de inativos.
- Top 20 cidades com maior número de clientes inativos.
- Salva resultados em CSV na pasta 'backups'.
"""

from pprint import pprint

import pandas as pd

from scripts.analise_clientes_pandas import carregar_clientes_dataframe


def analise_avancada(df: pd.DataFrame) -> None:
    # Normalizar valores nulos
    df = df.copy()
    df["status"] = df["status"].fillna("desconhecido")
    df["estado"] = df["estado"].fillna("(sem estado)")
    df["cidade"] = df["cidade"].fillna("(sem cidade)")

    print("\n===== VISÃO GERAL (STATUS) =====")
    status_counts = df["status"].value_counts(dropna=False)
    status_percent = (df["status"].value_counts(normalize=True) * 100).round(2)

    print("\nContagem por status:")
    print(status_counts)
    print("\nPercentual por status (%):")
    print(status_percent)

    # ----- Status por estado (UF) -----
    print("\n===== STATUS POR ESTADO (UF) =====")
    tabela_estado_status = (
        df.groupby(["estado", "status"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    # Garante que a coluna 'inativo' exista (caso raro de não haver inativos em algum estado)
    if "inativo" not in tabela_estado_status.columns:
        tabela_estado_status["inativo"] = 0

    tabela_estado_status["total"] = tabela_estado_status.sum(axis=1)
    tabela_estado_status["perc_inativos"] = (
        tabela_estado_status["inativo"] / tabela_estado_status["total"] * 100
    ).round(2)

    print("\nTabela de status por estado (primeiras linhas):")
    print(tabela_estado_status.head(10))

    # ----- Top 10 estados com maior % de inativos -----
    print("\n===== TOP 10 ESTADOS POR % DE INATIVOS =====")
    top_estados_inativos = tabela_estado_status.sort_values(
        by=["perc_inativos", "total"],
        ascending=[False, False],
    ).head(10)
    print(top_estados_inativos[["inativo", "total", "perc_inativos"]])

    # ----- Top 20 cidades com mais inativos -----
    print("\n===== TOP 20 CIDADES POR NÚMERO DE INATIVOS =====")
    df_inativos = df[df["status"] == "inativo"].copy()
    top_cidades_inativos = (
        df_inativos["cidade"]
        .value_counts()
        .head(20)
        .to_frame(name="quantidade_inativos")
    )
    print(top_cidades_inativos)

    # ----- Salvar CSVs em backups/ -----
    print("\nSalvando resultados em CSV na pasta 'backups'...")

    # 1) Status geral (contagem e percentuais)
    status_df = pd.DataFrame(
        {
            "quantidade": status_counts,
            "percentual": status_percent,
        }
    )
    status_df.to_csv("backups/analise_status_geral_pandas.csv", index_label="status")

    # 2) Status por estado (com total e % inativos)
    tabela_estado_status.to_csv(
        "backups/analise_status_por_estado_pandas.csv",
        index_label="estado",
    )

    # 3) Top 10 estados com maior % de inativos
    top_estados_inativos.to_csv(
        "backups/top_estados_percentual_inativos_pandas.csv",
        index_label="estado",
    )

    # 4) Top 20 cidades com maior número de inativos
    top_cidades_inativos.to_csv(
        "backups/top_cidades_inativos_pandas.csv",
        index_label="cidade",
    )

    print("✅ Arquivos CSV gerados com sucesso em 'backups/'.")


def main():
    df = carregar_clientes_dataframe()
    analise_avancada(df)


if __name__ == "__main__":
    main()
