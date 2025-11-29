from datetime import datetime
from config import get_collection

def main():
    col = get_collection().collection
    cur = col.find(
        {},
        {"_id": 0, "cpf": 1, "nome": 1, "data_cadastro": 1}
    ).sort([("data_cadastro", -1)]).limit(10)

    print("=== Últimos 10 clientes (mais recentes primeiro) ===")
    found = False
    for doc in cur:
        found = True
        data = doc.get("data_cadastro")
        # formata a data se vier como datetime
        if isinstance(data, datetime):
            data_fmt = data.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data_fmt = str(data)
        print(f"- CPF: {doc.get('cpf')} | Nome: {doc.get('nome')} | Cadastrado: {data_fmt}")

    if not found:
        print("⚠ Nenhum cliente encontrado. Tente rodar o teste de criação primeiro.")

if __name__ == "__main__":
    main()
