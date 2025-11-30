"""
Análises básicas de clientes usando Pandas em cima do MongoDB.

- Carrega todos os clientes não marcados para exclusão.
- Monta um DataFrame com campos principais (cpf, nome, status, cidade, estado).
- Exibe estatísticas simples (contagem por status, top cidades, top estados).
- Salva relatórios em CSV na pasta 'backups'.
"""

from pprint import pprint

import pandas as pd

from config import get_collection


def carregar_clientes_dataframe() -> pd.DataFrame:
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    try:
        print("Buscando documentos da coleção 'clientes' (ignorando marcados para exclusão)...")
        cursor = col.find(
            {"marcado_para_exclusao": {"$ne": True}},
            {
                "_id": 0,
                "cpf": 1,
                "nome": 1,
                "email": 1,
                "telefone": 1,
                "status": 1,
                "endereco": 1,
            },
        )

        rows = []
        for doc in cursor:
            endereco = doc.get("endereco") or {}
            rows.append(
                {
                    "cpf": doc.get("cpf"),
                    "nome": doc.get("nome"),
                    "email": doc.get("email"),
                    "telefone": doc.get("telefone"),
                    "status": doc.get("status"),
                    "cidade": endereco.get("cidade"),
                    "estado": endereco.get("estado"),
                    "cep": endereco.get("cep"),
                }
            )

        df = pd.DataFrame(rows)
        print(f"Total de clientes carregados no DataFrame: {len(df)}")
        return df

    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


def analise_basica(df: pd.DataFrame) -> None:
    print("\n===== VISÃO GERAL =====")
    print(f"Total de clientes: {len(df)}")
    print("Colunas:", list(df.columns))

    print("\n===== CONTAGEM POR STATUS =====")
    status_counts = df["status"].value_counts(dropna=False)
    print(status_counts)

    print("\n===== TOP 10 CIDADES (por quantidade de clientes) =====")
    cidades = (
        df["cidade"]
        .fillna("(sem cidade)")
        .value_counts()
        .head(10)
    )
    print(cidades)

    print("\n===== TOP 10 ESTADOS (por quantidade de clientes) =====")
    estados = (
        df["estado"]
        .fillna("(sem estado)")
        .value_counts()
        .head(10)
    )
    print(estados)

    print("\n===== AMOSTRA DE 5 LINHAS =====")
    pprint(df.head(5).to_dict(orient="records"))

    # ===== SALVAR RELATÓRIOS EM CSV =====
    print("\nSalvando relatórios em CSV na pasta 'backups'...")

    # 1) Contagem por status
    status_counts.to_frame(name="quantidade").to_csv(
        "backups/dashboard_status_pandas.csv",
        index_label="status",
    )

    # 2) Contagem por cidade
    (
        df["cidade"]
        .fillna("(sem cidade)")
        .value_counts()
        .to_frame(name="quantidade")
        .to_csv("backups/dashboard_cidades_pandas.csv", index_label="cidade")
    )

    # 3) Contagem por estado (UF)
    (
        df["estado"]
        .fillna("(sem estado)")
        .value_counts()
        .to_frame(name="quantidade")
        .to_csv("backups/dashboard_ufs_pandas.csv", index_label="estado")
    )

    print("✅ Relatórios salvos com sucesso.")


def main():
    df = carregar_clientes_dataframe()
    analise_basica(df)


if __name__ == "__main__":
    main()
