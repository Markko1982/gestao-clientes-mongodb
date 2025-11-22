from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Carrega o .env a partir da raiz do projeto
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

uri = os.getenv("MONGO_URI")
print("MONGO_URI:", uri)

client = MongoClient(uri)

db_names = client.list_database_names()
print("\nBancos encontrados:", db_names)

for dbname in db_names:
    db = client[dbname]
    print(f"\n=== DB: {dbname} ===")
    print("Coleções:", db.list_collection_names())
