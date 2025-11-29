from config import get_collection
import re

def so_digitos(s: str) -> bool:
    return bool(s) and re.fullmatch(r'\d+', s) is not None

def main():
    col = get_collection().collection
    total = col.count_documents({})
    apenas_digitos = 0
    com_pontuacao = 0

    # Varre de forma leve (poderíamos usar aggregation, mas iterar funciona bem em dev)
    for d in col.find({}, {"_id": 0, "cpf": 1}).limit(50000):
        cpf = d.get("cpf", "")
        if so_digitos(cpf):
            apenas_digitos += 1
        else:
            com_pontuacao += 1

    print(f"Total analisado: {apenas_digitos + com_pontuacao} (docs na coleção: {total})")
    print(f"- Somente dígitos: {apenas_digitos}")
    print(f"- Com pontuação/outros: {com_pontuacao}")

if __name__ == "__main__":
    main()
