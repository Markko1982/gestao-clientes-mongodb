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

    print("\n===== TOP 20 CIDADES POR NÚMERO DE INATIVOS =====")
    df_inativos = df[df["status"] == "inativo"].copy()

  # Agrupa por ESTADO + CIDADE
    top_cidades_inativos = (
    df_inativos
    .groupby(["estado", "cidade"])
    .size()
    .reset_index(name="quantidade_inativos")
    .sort_values(by="quantidade_inativos", ascending=False)
    .head(20)
    .reset_index(drop=True)   # índice 0..19 sem nome
)

    print(top_cidades_inativos)

    print("\n===== TOP 20 CIDADES POR % DE INATIVOS (mín. 50 clientes) =====")

    # Tabela com contagem de ativo/inativo por estado + cidade
    tabela_cidade_status = (
        df
        .groupby(["estado", "cidade"])["status"]
        .value_counts()
        .unstack(fill_value=0)  # vira colunas 'ativo', 'inativo'
        .reset_index()
    )

    # Garante que as colunas exista mesmo se não houver ninguém ativo/inativo em alguma cidade
    for col in ["ativo", "inativo"]:
        if col not in tabela_cidade_status.columns:
            tabela_cidade_status[col] = 0

    tabela_cidade_status["total"] = (
        tabela_cidade_status["ativo"] + tabela_cidade_status["inativo"]
    )

    # Filtra apenas cidades com um número mínimo de clientes (evita distorção)
    MIN_CLIENTES = 20
    tabela_filtrada = tabela_cidade_status[
        tabela_cidade_status["total"] >= MIN_CLIENTES
    ].copy()

    tabela_filtrada["perc_inativos"] = (
        tabela_filtrada["inativo"] / tabela_filtrada["total"] * 100
    ).round(2)

    top_cidades_perc_inativos = (
        tabela_filtrada
        .sort_values(by="perc_inativos", ascending=False)
        .head(50)
        .reset_index(drop=True)   # índice 0..19 sem nome
    )

    # Mostra só colunas relevantes na tela
    print(
        top_cidades_perc_inativos[
            ["estado", "cidade", "inativo", "total", "perc_inativos"]
        ]
    )

    # Salva CSV
    top_cidades_perc_inativos.to_csv(
        "backups/top_cidades_percentual_inativos_pandas.csv",
        index=False,
    )



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
    index=False  # salva estado, cidade e quantidade_inativos como colunas normais
)
    
        # Se não existe coluna 'idade', mas existe 'data_nascimento',
    # calcula idade em anos a partir da data de nascimento.
    if "idade" not in df.columns and "data_nascimento" in df.columns:
        df = df.copy()
        df["data_nascimento"] = pd.to_datetime(
    df["data_nascimento"],
    format="%Y-%m-%d",  # formato do nosso schema
    errors="coerce",
)


        hoje = pd.Timestamp("today").normalize()
        df["idade"] = ((hoje - df["data_nascimento"]).dt.days // 365)

    
    print("\n===== DISTRIBUIÇÃO POR FAIXA ETÁRIA =====")

    if "idade" not in df.columns:
                    print("⚠ Campo 'idade' não encontrado no DataFrame; relatório por faixa etária ignorado.")
    else:
                    df_idade = df.copy()

                    # Garante que idade é numérico
                    df_idade["idade"] = pd.to_numeric(df_idade["idade"], errors="coerce")
                    df_idade = df_idade.dropna(subset=["idade"])
                    df_idade = df_idade[df_idade["idade"] >= 0]

                    # Define faixas etárias
                    bins = [0, 18, 26, 36, 51, 66, 200]
                    labels = ["0-17", "18-25", "26-35", "36-50", "51-65", "66+"]

                    df_idade["faixa_etaria"] = pd.cut(
                        df_idade["idade"],
                        bins=bins,
                        labels=labels,
                        right=False,        # inclui o limite inferior, exclui o superior
                        include_lowest=True,
                    )

                    # Agrupa por faixa etária
                    tabela_faixa = (
                        df_idade["faixa_etaria"]
                        .value_counts()
                        .sort_index()
                        .rename_axis("faixa_etaria")
                        .to_frame("quantidade")
                    )

                    total_clientes = tabela_faixa["quantidade"].sum()
                    tabela_faixa["percentual"] = (
                        tabela_faixa["quantidade"] / total_clientes * 100
                    ).round(2)

                    print(tabela_faixa)

                    tabela_faixa.to_csv(
                        "backups/analise_faixa_etaria_pandas.csv",
                        index_label="faixa_etaria",
                    )


    print("\n===== TOP 10 DOMÍNIOS DE E-MAIL =====")

    # Extrai o domínio do e-mail: tudo depois do '@'
    df_emails = df.copy()
    df_emails["dominio_email"] = (
        df_emails["email"]
        .fillna("")
        .str.strip()
        .str.lower()
        .str.split("@")
        .str[-1]
    )

    # Considera apenas domínios que parecem válidos (contêm um ponto, ex: gmail.com)
    df_emails_validos = df_emails[
        df_emails["dominio_email"].str.contains(r"\.", regex=True)
    ]

    top_dominios_email = (
        df_emails_validos["dominio_email"]
        .value_counts()
        .head(10)
        .rename_axis("dominio")
        .to_frame("quantidade")
    )

    print(top_dominios_email)

    top_dominios_email.to_csv(
        "backups/top_dominios_email_pandas.csv",
        index_label="dominio",
    )




    print("✅ Arquivos CSV gerados com sucesso em 'backups/'.")


def main():
    df = carregar_clientes_dataframe()
    analise_avancada(df)


if __name__ == "__main__":
    main()
