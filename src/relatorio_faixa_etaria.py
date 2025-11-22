from collections import Counter
from datetime import date, datetime
from pathlib import Path
import csv
import sys

# Garante que a raiz do projeto esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection


def calcular_idade(data_nascimento):
    if not data_nascimento:
        return None

    # Se vier string, tenta converter
    if isinstance(data_nascimento, str):
        try:
            data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        except Exception:
            return None

    if isinstance(data_nascimento, datetime):
        data_nascimento = data_nascimento.date()

    hoje = date.today()
    return hoje.year - data_nascimento.year - (
        (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
    )


def faixa_etaria(idade):
    if idade is None:
        return "Sem data de nascimento"
    if idade < 18:
        return "Menores de 18"
    elif idade <= 25:
        return "18 a 25 anos"
    elif idade <= 35:
        return "26 a 35 anos"
    elif idade <= 45:
        return "36 a 45 anos"
    elif idade <= 60:
        return "46 a 60 anos"
    else:
        return "Acima de 60 anos"


def gerar_relatorio_faixa_etaria():
    col = get_collection()
    clientes = list(col.find({}))
    total = len(clientes)

    contagem = Counter()

    for cli in clientes:
        idade = calcular_idade(cli.get("data_nascimento"))
        contagem[faixa_etaria(idade)] += 1

    ordem = [
        "Menores de 18",
        "18 a 25 anos",
        "26 a 35 anos",
        "36 a 45 anos",
        "46 a 60 anos",
        "Acima de 60 anos",
        "Sem data de nascimento",
    ]

    print("============================================")
    print("RELATÓRIO DE CLIENTES POR FAIXA ETÁRIA")
    print("============================================\n")
    print(f"Total de clientes: {total}\n")
    print("Faixa etária                | Quantidade")
    print("-----------------------------------------+")

    # Pasta dados/ na raiz do projeto
    dados_dir = ROOT / "dados"
    dados_dir.mkdir(exist_ok=True)

    csv_path = dados_dir / "clientes_por_faixa_etaria.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["faixa_etaria", "quantidade"])
        for faixa in ordem:
            qtd = contagem.get(faixa, 0)
            print(f"{faixa:<27} | {qtd:>7}")
            writer.writerow([faixa, qtd])

    print(f"\nArquivo CSV gerado em: {csv_path}")


if __name__ == "__main__":
    gerar_relatorio_faixa_etaria()
