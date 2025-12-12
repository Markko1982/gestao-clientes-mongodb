from config import get_collection


def main():
    bundle = get_collection()
    col = bundle.collection  # pega a collection de dentro do bundle

    um = col.find_one()
    if not um:
        print("Nenhum documento encontrado na coleção 'clientes'.")
        return

    print("Um cliente qualquer:")
    print(um)
    print("\nCampos:", list(um.keys()))

    print("\nExemplo ativo=False:")
    print(col.find_one({"ativo": False}))

    print("\nExemplo status='INATIVO':")
    print(col.find_one({"status": "INATIVO"}))


if __name__ == "__main__":
    main()

