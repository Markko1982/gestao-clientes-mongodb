import os
from pymongo import MongoClient
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

uri = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/")
client = MongoClient(uri, serverSelectionTimeoutMS=3000)
try:
    print("Conectando em:", uri)
    print("Ping =>", client.admin.command("ping"))
    print("✓ Conexão OK")
finally:
    client.close()
