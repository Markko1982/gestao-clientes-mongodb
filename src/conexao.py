from pymongo import MongoClient
from config import MONGO_URI  # lê do .env via config.py

def conectar_mongodb():
    """
    Conecta ao MongoDB usando a URI centralizada no .env (via config.py).
    """
    try:
        cliente = MongoClient(MONGO_URI)
        # Teste rápido de conectividade
        cliente.admin.command('ping')
        print("✓ Conectado ao MongoDB com sucesso (config.py / .env)!")
        return cliente
    except Exception as erro:
        print(f"✗ Erro ao conectar ao MongoDB: {erro}")
        return None

# Teste rápido (execução direta)
if __name__ == "__main__":
    cliente = conectar_mongodb()
    if cliente:
        try:
            print(f"Bancos de dados disponíveis: {cliente.list_database_names()}")
        finally:
            cliente.close()
            print("✓ Conexão fechada")
