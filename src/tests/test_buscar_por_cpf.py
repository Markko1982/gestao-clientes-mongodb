import re
from src.cliente_crud import ClienteCRUD

def somente_digitos(cpf: str) -> str:
    return re.sub(r'\D+', '', cpf or '')

def main():
    crud = ClienteCRUD()

    raw = input("Digite o CPF (com ou sem pontuação): ").strip()
    cpf = somente_digitos(raw)

    if not cpf:
        print("✗ CPF vazio.")
        return

    print(f"Buscando por CPF normalizado: {cpf}")
    cliente = crud.buscar_por_cpf(cpf)

    if cliente:
        print("\n✓ Cliente encontrado:")
        print(cliente)
    else:
        print("\n✗ Nenhum cliente encontrado com esse CPF.")

    crud.fechar_conexao()

if __name__ == "__main__":
    main()
