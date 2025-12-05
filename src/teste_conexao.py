import os
from pymongo import MongoClient

try:
    # Tenta carregar variáveis do .env na raiz do projeto
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Se não tiver python-dotenv instalado, ignora silenciosamente
    pass

uri = os.getenv("MONGO_URI")
if not uri:
    raise RuntimeError(
        "Variável de ambiente MONGO_URI não definida.\n"
        "Defina MONGO_URI no arquivo .env na raiz do projeto "
        "ou exporte MONGO_URI no ambiente antes de rodar este script."
    )

client = MongoClient(uri, serverSelectionTimeoutMS=3000)

try:
    print("Conectando em:", uri)
    print("Ping =>", client.admin.command("ping"))
    print("✓ Conexão OK")
finally:
    client.close()
    print("✓ Conexão encerrada")
