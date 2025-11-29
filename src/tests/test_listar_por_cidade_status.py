from src.cliente_crud import ClienteCRUD

def main():
    cidade = input("Digite o nome (ou parte) da cidade: ").strip()
    status = input("Filtrar por status (ativo/inativo ou deixe vazio): ").strip().lower()

    filtro = {"endereco.cidade": {"$regex": cidade, "$options": "i"}}
    if status in ("ativo", "inativo"):
        filtro["status"] = status

    crud = ClienteCRUD()
    cur = crud.colecao.find(filtro, {"_id": 0, "nome": 1, "cpf": 1, "status": 1}) \
                      .sort("nome", 1) \
                      .limit(50)

    print("\n=== Resultados ===")
    count = 0
    for doc in cur:
        count += 1
        print(f"- {doc['nome']} | CPF: {doc['cpf']} | Status: {doc['status']}")
    if count == 0:
        print("⚠ Nenhum cliente encontrado.")
    else:
        print(f"\nTotal mostrado: {count}")

    crud.fechar_conexao()

if __name__ == "__main__":
    main()
