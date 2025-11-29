"""
Testa o validator $jsonSchema da coleção de clientes.

Cenários:
1) Cliente válido (deve passar)
2) Cliente com CPF inválido (deve falhar)
3) Cliente com status inválido (deve falhar)
4) Cliente sem campo obrigatório (telefone) (deve falhar)
"""

from datetime import datetime
from pprint import pprint

from pymongo.errors import WriteError
from config import get_collection


def run_test(label: str, doc: dict, should_pass: bool):
    """
    Tenta inserir um documento e compara com o resultado esperado.
    """
    bundle = get_collection()
    collection = bundle.collection

    print(f"\n==============================")
    print(f"Teste: {label}")
    print("==============================")
    print("Documento a inserir:")
    pprint(doc)

    try:
        result = collection.insert_one(doc)
        bundle.client.close()

        if should_pass:
            print("✅ Inserção PASSOU como esperado.")
            print("   _id inserido:", result.inserted_id)
        else:
            print("⚠️ Inserção PASSOU mas ERA para falhar!")
            print("   Verifique se o validator está correto.")
    except WriteError as e:
        bundle.client.close()
        if should_pass:
            print("❌ Inserção FALHOU mas era para PASSAR.")
        else:
            print("✅ Inserção FALHOU como esperado (validator funcionando).")

        details = getattr(e, "details", None)
        if details:
            print("Detalhes do erro de validação:")
            pprint(details)
        else:
            print("Mensagem de erro:")
            print(str(e))
    except Exception as e:
        bundle.client.close()
        print("❌ Erro inesperado ao inserir:")
        print(repr(e))


def main():
    # 1) Cliente válido
    cliente_valido = {
        "nome": "Cliente Válido do Schema",
        "cpf": "12345678901",  # 11 dígitos
        "email": "cliente.valido@example.com",
        "telefone": "11999990000",
        "status": "ativo",
        "endereco": {
            "rua": "Rua Teste",
            "numero": "123",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01000-000",
        },
        "data_cadastro": datetime.utcnow(),
    }

    # 2) CPF inválido (contém letras)
    cliente_cpf_invalido = {
        "nome": "Cliente CPF Invalido",
        "cpf": "12345abc901",  # inválido pelo regex
        "email": "cpf.invalido@example.com",
        "telefone": "11999990001",
        "status": "ativo",
        "endereco": {
            "rua": "Rua A",
            "numero": "10",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "20000-000",
        },
    }

    # 3) Status inválido
    cliente_status_invalido = {
        "nome": "Cliente Status Invalido",
        "cpf": "98765432100",
        "email": "status.invalido@example.com",
        "telefone": "21988880000",
        "status": "pendente",  # NÃO permitido pelo enum
        "endereco": {
            "rua": "Rua B",
            "numero": "50",
            "cidade": "Belo Horizonte",
            "estado": "MG",
            "cep": "30000-000",
        },
    }

    # 4) Sem campo obrigatório (telefone)
    cliente_sem_telefone = {
        "nome": "Cliente Sem Telefone",
        "cpf": "11223344556",
        "email": "sem.telefone@example.com",
        # "telefone" ausente → deve violar o required
        "status": "ativo",
        "endereco": {
            "rua": "Rua C",
            "numero": "100",
            "cidade": "Curitiba",
            "estado": "PR",
            "cep": "80000-000",
        },
    }

    run_test("1) Cliente válido (deve PASSAR)", cliente_valido, should_pass=True)
    run_test("2) CPF inválido (deve FALHAR)", cliente_cpf_invalido, should_pass=False)
    run_test("3) Status inválido (deve FALHAR)", cliente_status_invalido, should_pass=False)
    run_test("4) Sem telefone (deve FALHAR)", cliente_sem_telefone, should_pass=False)


if __name__ == "__main__":
    main()
