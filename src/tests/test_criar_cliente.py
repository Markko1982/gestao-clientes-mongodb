from datetime import datetime
from src.cliente_model import Cliente
from src.cliente_crud import ClienteCRUD

def gerar_cpf_unico():
    # Gera 11 dígitos baseados no horário (para evitar duplicidade)
    seed = datetime.now().strftime("%H%M%S%f")  # ex: 215959123456
    return (seed[-11:]).rjust(11, "0")

def main():
    cpf = gerar_cpf_unico()
    doc = Cliente(
        nome="Cliente Teste CRUD",
        cpf=cpf,
        email="cliente.teste@example.com",
        telefone="11988887777",
        data_nascimento="1990-05-15",
        endereco={
            "rua": "Rua Alpha",
            "numero": "100",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "estado": "SP",
            "cep": "01000-000",
        },
        status="ativo",
    )

    crud = ClienteCRUD()
    ok = crud.criar_cliente(doc)
    print("CPF usado:", cpf)
    crud.fechar_conexao()
    print("Resultado da criação:", ok)

if __name__ == "__main__":
    main()
