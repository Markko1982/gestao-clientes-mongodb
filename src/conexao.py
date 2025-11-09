from pymongo import MongoClient

def conectar_mongodb():
    """
    Conecta ao MongoDB rodando no Docker
    """
    try:
        # String de conexão
        # Usuário: admin, Senha: admin123
        uri = "mongodb://admin:admin123@localhost:27017/"
        
        # Criar cliente MongoDB
        cliente = MongoClient(uri)
        
        # Testar conexão
        cliente.admin.command('ping')
        print("✓ Conectado ao MongoDB com sucesso!")
        
        return cliente
        
    except Exception as erro:
        print(f"✗ Erro ao conectar ao MongoDB: {erro}")
        return None

# Testar a conexão
if __name__ == "__main__":
    cliente = conectar_mongodb()
    if cliente:
        print(f"Bancos de dados disponíveis: {cliente.list_database_names()}")
        cliente.close()
