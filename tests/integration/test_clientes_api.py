# tests/integration/test_clientes_api.py

def test_criar_cliente_salva_no_mongo(client, mongo_collection):
    """
    Cenário:
      - Envia um POST /clientes com dados válidos
      - Verifica que a API responde 201
      - Confere que o cliente foi gravado no MongoDB
    """
    payload = {
        "cpf": "12345678901",
        "nome": "João da Silva",
        "email": "joao.silva@example.com",
        "telefone": "11999990000",
        "status": "ativo",
        "data_nascimento": "1980-01-01",
        "endereco": {
            "rua": "Rua A",
            "numero": "123",
            "complemento": "Apto 1",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01000-000",
        },
    }

    # 1) Chama o endpoint da API
    response = client.post("/clientes", json=payload)

    # 2) Valida resposta HTTP
    assert response.status_code == 201

    body = response.json()
    # Deve vir com um id gerado e refletir os dados de entrada
    assert "id" in body
    assert isinstance(body["id"], str)
    assert body["cpf"] == payload["cpf"]
    assert body["nome"] == payload["nome"]
    assert body["email"] == payload["email"]
    assert body["telefone"] == payload["telefone"]
    # status pode vir default "ativo" se a API sobrescrever
    assert body.get("status") == "ativo"

    # 3) Valida que o documento existe no MongoDB
    doc = mongo_collection.find_one({"cpf": payload["cpf"]})
    assert doc is not None
    assert doc["cpf"] == payload["cpf"]
    assert doc["nome"] == payload["nome"]
    assert doc["email"] == payload["email"]
    assert doc["telefone"] == payload["telefone"]
    assert doc.get("endereco", {}).get("cidade") == payload["endereco"]["cidade"]
