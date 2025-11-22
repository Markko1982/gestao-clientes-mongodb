from pathlib import Path
import csv
import sys

# Garante que o diretório raiz esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection


ARQUIVO = ROOT / "dados" / "clientes_inativos.csv"


def exportar_inativos_csv() -> None:
    col = get_collection()

    filtro = {"status": "inativo"}

    # Conta quantos inativos existem
    total = col.count_documents(filtro)

    # Garante que a pasta "dados" exista
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)

    with ARQUIVO.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")

        # Cabeçalho do CSV
        writer.writerow([
            "nome",
            "cpf",
            "email",
            "telefone",
            "data_nascimento",
            "rua",
            "numero",
            "bairro",
            "cidade",
            "estado",
            "cep",
            "status",
            "data_cadastro",
        ])

        # Exporta apenas clientes com status INATIVO
        for cli in col.find(filtro).sort("nome"):
            end = cli.get("endereco", {}) or {}

            writer.writerow([
                cli.get("nome", ""),
                cli.get("cpf", ""),
                cli.get("email", ""),
                cli.get("telefone", ""),
                cli.get("data_nascimento", ""),
                end.get("rua", ""),
                end.get("numero", ""),
                end.get("bairro", ""),
                end.get("cidade", ""),
                end.get("estado", ""),
                end.get("cep", ""),
                cli.get("status", ""),
                cli.get("data_cadastro", ""),
            ])

    print("✔ Arquivo gerado: dados/clientes_inativos.csv")
    print(f"  Total de clientes inativos exportados: {total}")
    input("\nPressione ENTER para voltar ao menu...")
    

if __name__ == "__main__":
    exportar_inativos_csv()
