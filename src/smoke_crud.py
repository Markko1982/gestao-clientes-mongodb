"""
Smoke test do ClienteCRUD.

- Conta clientes antes
- Insere um cliente de teste com CPF aleatório
- Conta clientes depois
- Busca por CPF e por nome
"""

from pathlib import Path
import sys
import random

# Ajuste de caminhos para conseguir importar a partir de src/ e raiz
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from cliente_crud import ClienteCRUD
from cliente_model import Cliente


def gerar_cpf_aleatorio() -> str:
    """Gera um CPF aleatório de 11 dígitos (sem validação de dígitos verificadores)."""
    return "".join(str(random.randint(0, 9)) for _ in range(11))


def main():
    crud = ClienteCRUD()
    try:
        total_antes = crud.contar_clientes()
        print(f"Total de clientes ANTES do teste: {total_antes}")

        cpf_teste = gerar_cpf_aleatorio()
        nome_teste = f"Cliente Smoke {cpf_teste[-4:]}"
        email_teste = f"smoke{cpf_teste[-4:]}@example.com"

        endereco_teste = {
            "rua": "Rua do Smoke Test",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "Curitiba",
            "estado": "PR",
            "cep": "80000-000",
        }

        cliente = Cliente(
            nome=nome_teste,
            cpf=cpf_teste,
            email=email_teste,
            telefone="41999990000",
            data_nascimento="1990-01-01",
            endereco=endereco_teste,
        )

        print(f"\nInserindo cliente de teste com CPF {cpf_teste} ...")
        ok = crud.criar_cliente(cliente)
        print(f"Inserção OK? {ok}")

        total_depois = crud.contar_clientes()
        print(f"\nTotal de clientes DEPOIS do teste: {total_depois}")

        if ok:
            print("\nBuscando pelo CPF recém-criado...")
            achado = crud.buscar_por_cpf(cpf_teste)
            print("Resultado da busca por CPF:", achado)

            print("\nBuscando por nome parcial 'Cliente Smoke' (mostrando até 3):")
            encontrados = crud.buscar_por_nome("Cliente Smoke")
            for c in encontrados[:3]:
                print(" -", c)

    finally:
        crud.fechar_conexao()


if __name__ == "__main__":
    main()
