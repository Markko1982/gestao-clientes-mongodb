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
            "cidade": "São Paulo",
            "estado": "SP",
        },
    }

    # 1) Envia requisição para criar o cliente
    resp = client.post("/clientes", json=payload)

    # 2) Valida resposta HTTP
    assert resp.status_code == 201
    body = resp.json()

    # 2.1) Confere alguns campos básicos
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


def test_obter_cliente_por_cpf_retorna_cliente_salvo_no_mongo(client, mongo_collection):
    """
    Cenário:
      - Cria um cliente via POST /clientes
      - Busca o mesmo cliente via GET /clientes/{cpf}
      - Confere que os dados batem com o payload enviado
    """
    payload = {
        "cpf": "11111111111",
        "nome": "Cliente Buscar CPF",
        "email": "buscar.cpf@example.com",
        "telefone": "11999990001",
        "status": "ativo",
        "endereco": {
            "cidade": "São Paulo",
            "estado": "SP",
        },
    }

    # 1) Cria o cliente
    resp_create = client.post("/clientes", json=payload)
    assert resp_create.status_code == 201

    # 2) Busca o cliente pelo CPF
    resp_get = client.get(f"/clientes/{payload['cpf']}")
    assert resp_get.status_code == 200

    body = resp_get.json()
    assert body["cpf"] == payload["cpf"]
    assert body["nome"] == payload["nome"]
    assert body["email"] == payload["email"]
    assert body["telefone"] == payload["telefone"]
    assert body.get("status") == "ativo"
    assert body.get("endereco", {}).get("cidade") == payload["endereco"]["cidade"]
    assert body.get("endereco", {}).get("estado") == payload["endereco"]["estado"]


def test_obter_cliente_por_cpf_inexistente_retorna_404(client):
    """
    Cenário:
      - Tenta buscar um CPF que não existe
      - Espera resposta 404 com mensagem apropriada
    """
    resp = client.get("/clientes/00000000000")

    assert resp.status_code == 404
    body = resp.json()
    assert body["detail"] == "Cliente não encontrado."


def test_listar_clientes_filtrando_por_status_e_localizacao(client, mongo_collection):
    """
    Cenário:
      - Cria dois clientes:
          * um ATIVO em São Paulo/SP
          * um INATIVO em outra cidade/estado
      - Chama GET /clientes filtrando por status=ativo, estado=SP, cidade="São Paulo"
      - Confere que somente o cliente esperado aparece na lista
    """
    payload_ativo_sp = {
        "cpf": "22222222222",
        "nome": "Cliente Ativo SP",
        "email": "ativo.sp@example.com",
        "telefone": "11999990002",
        "status": "ativo",
        "endereco": {
            "cidade": "São Paulo",
            "estado": "SP",
        },
    }

    payload_inativo_rj = {
        "cpf": "33333333333",
        "nome": "Cliente Inativo RJ",
        "email": "inativo.rj@example.com",
        "telefone": "21999990003",
        "status": "inativo",
        "endereco": {
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
        },
    }

    # 1) Cria os dois clientes
    resp1 = client.post("/clientes", json=payload_ativo_sp)
    resp2 = client.post("/clientes", json=payload_inativo_rj)
    assert resp1.status_code == 201
    assert resp2.status_code == 201

    # 2) Lista clientes filtrando por status/estado/cidade
    resp_list = client.get(
        "/clientes",
        params={
            "status": "ativo",
            "estado": "SP",
            "cidade": "São Paulo",
        },
    )

    assert resp_list.status_code == 200
    body = resp_list.json()

    # A resposta deve ser uma lista
    assert isinstance(body, list)
    assert len(body) >= 1

    cpfs = {cliente["cpf"] for cliente in body}

    # Deve conter o cliente ativo de SP
    assert payload_ativo_sp["cpf"] in cpfs
    # Não deve conter o cliente inativo de RJ
    assert payload_inativo_rj["cpf"] not in cpfs
