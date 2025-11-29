import re
from src.cliente_crud import ClienteCRUD

def somente_digitos(cpf: str) -> str:
    import re
    return re.sub(r'\D+', '', cpf or '')

def main():
    raw = input("Digite o CPF do cliente a atualizar (com ou sem pontuação): ").strip()
    cpf = somente_digitos(raw)
    if not cpf:
        print("✗ CPF vazio.")
        return

    crud = ClienteCRUD()
    cliente = crud.buscar_por_cpf(cpf)
    if not cliente:
        print("✗ Cliente não encontrado para o CPF informado.")
        crud.fechar_conexao()
        return

    print(f"Cliente: {cliente.nome} | CPF: {cliente.cpf} | Status atual: {cliente.status}")

    # Alterna o status
    novo_status = "inativo" if cliente.status != "inativo" else "ativo"
    ok = crud.atualizar_cliente(cpf, {"status": novo_status})

    if ok:
        cliente2 = crud.buscar_por_cpf(cpf)
        print(f"✓ Status atualizado: {cliente2.status}")
    else:
        print("✗ Falha ao atualizar o status.")

    crud.fechar_conexao()

if __name__ == "__main__":
    main()
