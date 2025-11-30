from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from config import get_collection


# Obter conexão com MongoDB (um único client para toda a API)
_bundle = get_collection()
_client = _bundle.client
_db = _bundle.db
_collection = _bundle.collection


class Endereco(BaseModel):
    rua: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    cep: Optional[str] = None


class ClienteBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: str
    status: str = Field("ativo", pattern="^(ativo|inativo)$")
    endereco: Endereco


class ClienteCreate(ClienteBase):
    cpf: str = Field(..., min_length=11, max_length=11)


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ativo|inativo)$")
    endereco: Optional[Endereco] = None


class ClienteOut(ClienteBase):
    id: str
    cpf: str


def _doc_to_cliente_out(doc) -> ClienteOut:
    return ClienteOut(
        id=str(doc.get("_id")),
        cpf=doc["cpf"],
        nome=doc["nome"],
        email=doc["email"],
        telefone=doc["telefone"],
        status=doc.get("status", "ativo"),
        endereco=doc.get("endereco", {}) or {},
    )


app = FastAPI(
    title="API de Clientes - MongoDB",
    version="0.1.0",
    description="API REST simples para gestão de clientes usando MongoDB.",
)


@app.get("/health")
def health_check():
    """Endpoint simples para verificar se a API e o Mongo estão OK."""
    try:
        _db.command("ping")
        total = _collection.count_documents({"marcado_para_exclusao": {"$ne": True}})
        return {
            "status": "ok",
            "database": _db.name,
            "collection": _collection.name,
            "total_clientes": total,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clientes/{cpf}", response_model=ClienteOut)
def obter_cliente_por_cpf(cpf: str):
    """Busca um cliente pelo CPF (11 dígitos)."""
    doc = _collection.find_one(
        {"cpf": cpf, "marcado_para_exclusao": {"$ne": True}}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return _doc_to_cliente_out(doc)


@app.get("/clientes", response_model=List[ClienteOut])
def listar_clientes(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    cidade: Optional[str] = None,
):
    """Lista clientes com paginação simples e filtros opcionais."""
    filtro: dict = {"marcado_para_exclusao": {"$ne": True}}

    if status:
        if status not in ("ativo", "inativo"):
            raise HTTPException(
                status_code=400,
                detail="Status inválido. Use 'ativo' ou 'inativo'.",
            )
        filtro["status"] = status

    if cidade:
        filtro["endereco.cidade"] = cidade

    cursor = (
        _collection.find(filtro)
        .skip(max(skip, 0))
        .limit(min(max(limit, 1), 100))
    )

    docs = list(cursor)
    return [_doc_to_cliente_out(d) for d in docs]


@app.post("/clientes", response_model=ClienteOut, status_code=201)
def criar_cliente(cliente: ClienteCreate):
    """Cria um novo cliente. CPF deve ser único."""
    data = cliente.model_dump()
    # endereço vem como Endereco → convertemos para dict bruto
    data["endereco"] = cliente.endereco.model_dump()

    try:
        result = _collection.insert_one(data)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Já existe um cliente cadastrado com esse CPF.",
        )

    doc = _collection.find_one({"_id": result.inserted_id})
    return _doc_to_cliente_out(doc)


@app.patch("/clientes/{cpf}", response_model=ClienteOut)
def atualizar_cliente(cpf: str, atualizacao: ClienteUpdate):
    """Atualiza parcialmente um cliente identificando pelo CPF."""
    update_data = atualizacao.model_dump(exclude_unset=True)

    if "endereco" in update_data and update_data["endereco"] is not None:
        update_data["endereco"] = update_data["endereco"].model_dump()

    if not update_data:
        raise HTTPException(
            status_code=400, detail="Nenhum campo para atualizar foi enviado."
        )

    res = _collection.update_one(
        {"cpf": cpf, "marcado_para_exclusao": {"$ne": True}},
        {"$set": update_data},
    )

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    doc = _collection.find_one({"cpf": cpf})
    return _doc_to_cliente_out(doc)


@app.delete("/clientes/{cpf}", status_code=204)
def deletar_cliente(cpf: str):
    """Inativa e marca o cliente para exclusão (soft delete)."""
    res = _collection.update_one(
        {"cpf": cpf},
        {"$set": {"status": "inativo", "marcado_para_exclusao": True}},
    )

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    return Response(status_code=204)


@app.on_event("shutdown")
def fechar_conexao_mongo():
    """Garante que o client do Mongo seja fechado ao desligar a API."""
    _client.close()
