"""
Aplica (ou atualiza) o validator $jsonSchema na coleção de clientes.

- Usa as configs de conexão definidas em config.py
- Garante que a coleção existe antes de chamar collMod
- Define:
    - campos obrigatórios: nome, cpf, email, telefone, status, endereco
    - tipos básicos corretos (string, object, date)
    - cpf: exatamente 11 dígitos numéricos
    - status: apenas "ativo" ou "inativo"
- validationLevel = "moderate": NÃO valida documentos antigos armazenados,
  apenas novos inserts/updates após a aplicação.
"""

from pprint import pprint

from pymongo.errors import OperationFailure
from config import get_collection  # usa helper centralizado de conexão


def build_validator():
    """
    Monta o jsonSchema usado pelo MongoDB para validar documentos
    da coleção de clientes.

    Regras principais:
    - nome: obrigatório, string
    - cpf: obrigatório, string com exatamente 11 dígitos numéricos
    - status: obrigatório, apenas "ativo", "inativo" ou "excluido"
    - endereco: obrigatório, com campos estado e cidade como strings
    """
    return {
        "$jsonSchema": {
            "bsonType": "object",
            # Campos obrigatórios mínimos
            "required": ["nome", "cpf", "status", "endereco"],
            "properties": {
                "nome": {
                    "bsonType": "string",
                    "description": "Nome completo do cliente (obrigatório).",
                },
                "cpf": {
                    "bsonType": "string",
                    "pattern": "^[0-9]{11}$",
                    "description": "CPF com exatamente 11 dígitos numéricos.",
                },
                # Mantemos data_nascimento opcional, mas validada quando vier
                "data_nascimento": {
                    "bsonType": ["string", "null"],
                    "description": "Data de nascimento no formato YYYY-MM-DD ou null.",
                    "pattern": r"^\d{4}-\d{2}-\d{2}$",
                },
                # Outros campos continuam existindo, mas não são 'required'
                "email": {
                    "bsonType": "string",
                    "description": "E-mail do cliente (texto simples; validação mais forte fica na aplicação).",
                },
                "telefone": {
                    "bsonType": "string",
                    "description": "Telefone de contato (validado só como string aqui).",
                },
                "status": {
                    "bsonType": "string",
                    "enum": ["ativo", "inativo", "excluido"],
                    "description": "Status do cliente (ativo, inativo ou excluido).",
                },
                "endereco": {
                    "bsonType": "object",
                    "description": "Endereço completo do cliente.",
                    # Garante que estado e cidade existem e são strings
                    "required": ["estado", "cidade"],
                    "properties": {
                        "estado": {
                            "bsonType": "string",
                            "description": "UF do estado (ex: SP, RJ).",
                        },
                        "cidade": {
                            "bsonType": "string",
                            "description": "Nome da cidade.",
                        },
                    },
                    # Permitimos outros campos dentro de endereco (rua, cep etc.)
                    "additionalProperties": True,
                },
                "data_cadastro": {
                    "bsonType": ["date", "null"],
                    "description": "Data de cadastro; se informado, deve ser um Date ou null.",
                },
            },
            # Permitimos outros campos além dos descritos acima no documento raiz.
            "additionalProperties": True,
        }
    }



def show_current_validator(db, collection_name: str):
    """
    Mostra o validator atual da coleção (se existir).
    """
    info = db.command("listCollections", filter={"name": collection_name})
    first_batch = info.get("cursor", {}).get("firstBatch", [])
    if not first_batch:
        print(f"Nenhuma coleção encontrada com o nome: {collection_name!r}")
        return

    options = first_batch[0].get("options", {})
    current_validator = options.get("validator")
    print("\nValidator atual da coleção (pode ser None se não houver):")
    pprint(current_validator)


def ensure_collection_exists(db, collection_name: str):
    """
    Garante que a coleção existe fisicamente no banco.
    Se ainda não existe, cria vazia.
    """
    if collection_name not in db.list_collection_names():
        print(f"Coleção {collection_name!r} ainda não existe. Criando vazia...")
        db.create_collection(collection_name)
        print("Coleção criada.\n")
    else:
        print(f"Coleção {collection_name!r} já existe.\n")


def apply_validator():
    """
    Fluxo principal:
    - conecta no Mongo
    - mostra validator atual
    - aplica novo validator via collMod
    - mostra resultado
    """
    # get_collection retorna um bundle (client, db, collection)
    bundle = get_collection()
    client = bundle.client
    db = bundle.db
    collection = bundle.collection
    collection_name = collection.name

    print(f"Conectado ao banco: {db.name}, coleção: {collection_name}")

    try:
        ensure_collection_exists(db, collection_name)
        show_current_validator(db, collection_name)

        new_validator = build_validator()
        print("\nNovo validator que será aplicado:")
        pprint(new_validator)

        print("\nAplicando validator via collMod (validationLevel='moderate', validationAction='error')...")
        result = db.command(
            "collMod",
            collection_name,
            validator=new_validator,
            validationLevel="moderate",
            validationAction="error",
        )

        print("\nResultado do collMod:")
        pprint(result)

        print("\nValidator após collMod:")
        show_current_validator(db, collection_name)

        print(
            "\n✅ Validator aplicado com sucesso.\n"
            "Novos documentos/updates precisarão respeitar o jsonSchema definido.\n"
            "Documentos antigos permanecem como estão (validationLevel='moderate')."
        )

    except OperationFailure as e:
        print("\n❌ ERRO ao aplicar validator:")
        # OperationFailure costuma trazer detalhes úteis em .details
        details = getattr(e, "details", None)
        if details:
            pprint(details)
        else:
            print(str(e))
    finally:
        client.close()
        print("\nConexão com o MongoDB fechada.")


if __name__ == "__main__":
    apply_validator()
