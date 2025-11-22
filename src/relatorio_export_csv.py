import os
import sys
import csv

# Garante que a pasta raiz do projeto esteja no sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # .../gestao-clientes-mongodb/src
ROOT_DIR = os.path.dirname(BASE_DIR)                      # .../gestao-clientes-mongodb
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import get_collection


def exportar_clientes_csv():
    col = get_collection()

    total = col.count_documents({})
    if total == 0:
        print("Nenhum cliente encontrado no banco.")
        input("Pressione ENTER para voltar ao menu...")
        return

    # Garante que a pasta 'dados' exista
    os.makedirs("dados", exist_ok=True)
    caminho = os.path.join("dados", "clientes_export.csv")

    # Busca todos os documentos
    cursor = col.find({})

    # Pega o primeiro documento para descobrir os campos
    first = cursor.next()
    campos = list(first.keys())

    # Se não quiser exportar o _id, descomente estas linhas:
    # if "_id" in campos:
    #     campos.remove("_id")

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        # Cabeçalho
        writer.writerow(campos)

        # Primeiro registro
        writer.writerow([first.get(c, "") for c in campos])

        # Demais registros
        for doc in cursor:
            writer.writerow([doc.get(c, "") for c in campos])

    print(f"✅ Arquivo gerado: {caminho}")
    print(f"   Total de clientes exportados: {total}")
    input("Pressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    exportar_clientes_csv()
