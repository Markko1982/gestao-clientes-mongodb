from pathlib import Path
import sys
import os

# Garante que o diretório raiz esteja no sys.path para importar config
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection


def limpar_tela():
    os.system("clear" if os.name == "posix" else "cls")


def pausar():
    input("Pressione ENTER para voltar ao menu...")


def main():
    limpar_tela()

    col = get_collection()

    # IMPORTANTE: inativos são marcados com status = "inativo"
    filtro = {"status": "inativo"}

    total = col.count_documents(filtro)

    if total == 0:
        print("⚠ Nenhum cliente inativo encontrado.")
        pausar()
        return

    print("==============================================")
    print(" RELATÓRIO DE CLIENTES INATIVOS")
    print("==============================================")
    print(f"Total de clientes inativos: {total}\n")

    # Mostra no máximo 20 exemplos só para visualização
    for cli in col.find(filtro).limit(20):
        print(f"- {cli.get('nome')} | CPF: {cli.get('cpf')} | status: {cli.get('status')}")

    print("\n(Exibidos no máximo 20 clientes.)\n")
    pausar()


if __name__ == "__main__":
    main()
