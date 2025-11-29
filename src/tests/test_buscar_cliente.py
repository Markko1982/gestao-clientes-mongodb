from src.cliente_crud import ClienteCRUD

def main():
    crud = ClienteCRUD()

    # Cole o CPF impresso no teste anterior aqui:
    cpf_para_buscar = input("Digite o CPF para buscar: ").strip()

    cliente = crud.buscar_por_cpf(cpf_para_buscar)
    if cliente:
        print("\n✓ Cliente encontrado:")
        print(cliente)
    else:
        print("\n✗ Nenhum cliente encontrado com esse CPF.")

    print("\nTotal de clientes cadastrados:", crud.contar_clientes({}))
    crud.fechar_conexao()

if __name__ == "__main__":
    main()
