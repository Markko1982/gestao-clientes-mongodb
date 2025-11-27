from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import os


# Diretório raiz do projeto (onde está este config.py e o .env)
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# URL de conexão com o MongoDB (vem do .env ou usa padrão)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@localhost:27017/")

# Nome do banco e da coleção padrão
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "empresa_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "clientes")


def get_collection():
    """
    Abre conexão com o Mongo e retorna (client, db, collection)
    usando empresa_db.clientes (ou os valores do .env, se definidos).
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    return client, db, collection
# --- Helper para compatibilidade de get_collection --------------------
class _CollectionBundle:
    """Objeto que representa (client, db, collection) ao mesmo tempo.

    - Pode ser desempacotado:
        client, db, col = get_collection()
    - Pode ser usado como se fosse a própria coleção:
        col = get_collection()
        total = col.count_documents({})
    """
    def __init__(self, client, db, collection):
        self.client = client
        self.db = db
        self.collection = collection

    def __iter__(self):
        # permite: client, db, col = get_collection()
        yield self.client
        yield self.db
        yield self.collection

    def __getattr__(self, name):
        # delega chamadas para a coleção real
        return getattr(self.collection, name)

    def __getitem__(self, idx):
        return (self.client, self.db, self.collection)[idx]

    def __len__(self):
        return 3

    def __repr__(self):
        return f"<CollectionBundle db={self.db.name!r} collection={self.collection.name!r}>"

def get_collection():
    """Retorna um objeto compatível com o uso antigo e o novo.

    - col = get_collection()
    - client, db, col = get_collection()
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    return _CollectionBundle(client, db, collection)
