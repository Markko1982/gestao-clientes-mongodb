import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

# Usa a mesma URI do projeto
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/")


def pick_db_and_collection(client):
    """
    Escolhe automaticamente o DB e a coleção de clientes.
    - Procura por DB com 'cliente' no nome.
    - Dentro dele, procura coleção com 'cliente' no nome.
    """
    prefer_db = None
    for dbname in client.list_database_names():
        if "cliente" in dbname.lower():
            prefer_db = dbname
            break

    if not prefer_db:
        # fallback se nada casar
        prefer_db = "test"

    db = client[prefer_db]

    colname = None
    names = db.list_collection_names()
    for n in names:
        if "cliente" in n.lower():
            colname = n
            break

    if not colname and names:
        colname = names[0]

    if not colname:
        print("⚠ Não encontrei coleção de clientes. Cadastre um cliente ou gere dados primeiro.")
        return None, db

    return db[colname], db


def main():
    client = MongoClient(MONGO_URI)
    col, db = pick_db_and_collection(client)

    if not col:
        client.close()
        return

    print("DB escolhido:", db.name)
    print("Coleção escolhida:", col.name)

    # Índice único em CPF
    col.create_index("cpf", unique=True)
    print("✔ Índice único em cpf criado/garantido.")

    # Índice auxiliar para buscas por cidade + nome
    col.create_index([("cidade", ASCENDING), ("nome", ASCENDING)])
    print("✔ Índice em (cidade, nome) criado/garantido.")

    print("✅ Setup de índices concluído.")
    client.close()


if __name__ == "__main__":
    main()
