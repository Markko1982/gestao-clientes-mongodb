from pathlib import Path
import sys

# Garante que o diretório raiz esteja no sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection


def main():
    col = get_collection()

    um = col.find_one()
    print("Um cliente qualquer:")
    print(um)
    print("\nCampos:", list(um.keys()))

    print("\nExemplo ativo=False:")
    print(col.find_one({"ativo": False}))

    print("\nExemplo status='INATIVO':")
    print(col.find_one({"status": "INATIVO"}))


if __name__ == "__main__":
    main()
