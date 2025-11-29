"""
Teste para confirmar que o ClienteCRUD ignora documentos
com marcado_para_exclusao = True.
"""

from pathlib import Path
import sys
from pprint import pprint

# Garante raiz e src no sys.path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from config import get_collection
from cliente_crud import ClienteCRUD


def main():
    # Conexão crua (pra ver total bruto)
    bundle = get_collection()
    col = bundle.collection

    try:
        total_bruto = col.count_documents({})
        total_marcados = col.count_documents({"marcado_para_exclusao": True})
        print(f"Total de documentos na coleção (bruto)         : {total_bruto}")
        print(f"Total com marcado_para_exclusao = True         : {total_marcados}")

    finally:
        bundle.client.close()

    print("\n--- Usando ClienteCRUD (deve ignorar marcados_para_exclusao) ---\n")

    crud = ClienteCRUD()
    try:
        total_crud = crud.contar_clientes()
        print(f"Total contado via ClienteCRUD.contar_clientes(): {total_crud}")

        print("\nAlguns clientes retornados por listar_todos():")
        for cliente in crud.listar_todos()[:5]:
            pprint(
                {
                    "nome": cliente.nome,
                    "cpf": cliente.cpf,
                    "status": cliente.status,
                }
            )

    finally:
        crud.fechar_conexao()


if __name__ == "__main__":
    main()
