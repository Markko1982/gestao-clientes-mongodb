from config import get_collection

def main():
    col = get_collection().collection
    print("=== Amostra de CPFs salvos (primeiros 15) ===")
    for d in col.find({}, {"_id": 0, "nome": 1, "cpf": 1}).limit(15):
        print(f"- Nome: {d.get('nome')} | CPF salvo: {d.get('cpf')}")
    print("\nTotal de docs:", col.count_documents({}))

if __name__ == "__main__":
    main()
