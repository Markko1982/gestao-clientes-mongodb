from src.cliente_crud import ClienteCRUD

def main():
    termo = input("Digite parte do nome para buscar: ").strip()
    if not termo:
        print("✗ Termo de busca vazio.")
        return

    crud = ClienteCRUD()
    resultados = crud.buscar_por_nome(termo)

    if resultados:
        print(f"\n✓ {len(resultados)} cliente(s) encontrado(s):")
        for c in resultados:
            print(f"- Nome: {c.nome} | CPF: {c.cpf} | Status: {c.status}")
    else:
        print("\n✗ Nenhum cliente encontrado com esse nome.")

    crud.fechar_conexao()

if __name__ == "__main__":
    main()
