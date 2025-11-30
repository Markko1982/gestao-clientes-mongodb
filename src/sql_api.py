from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .sql_db import get_db
from .sql_models import Cliente


# ====== MODELOS Pydantic (entrada/saída) ======

class EnderecoIn(BaseModel):
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
    endereco: EnderecoIn


class ClienteCreate(ClienteBase):
    cpf: str = Field(..., min_length=11, max_length=11)


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ativo|inativo)$")
    endereco: Optional[EnderecoIn] = None


class ClienteOut(ClienteBase):
    id: int
    cpf: str


# ====== Função auxiliar para converter model SQL -> Pydantic ======

def cliente_to_out(model: Cliente) -> ClienteOut:
    return ClienteOut(
        id=model.id,
        cpf=model.cpf,
        nome=model.nome,
        email=model.email,
        telefone=model.telefone,
        status=model.status,
        endereco=model.endereco or {},
    )


# ====== Instância da aplicação FastAPI ======

app = FastAPI(
    title="API de Clientes - PostgreSQL",
    version="0.1.0",
    description="Exemplo de API REST usando FastAPI + SQLAlchemy + PostgreSQL.",
)


# ====== Endpoints ======

@app.get("/sql/health")
def health_check(db: Session = Depends(get_db)):
    """
    Verifica se a API consegue se conectar ao PostgreSQL.
    """
    # Teste simples: contar quantos clientes existem na tabela
    total = db.query(Cliente).count()
    return {
        "status": "ok",
        "database": "PostgreSQL",
        "tabela": Cliente.__tablename__,
        "total_clientes": total,
    }


@app.get("/sql/clientes/{cpf}", response_model=ClienteOut)
def obter_cliente_por_cpf(cpf: str, db: Session = Depends(get_db)):
    """
    Busca um cliente pelo CPF (11 dígitos) no PostgreSQL.
    """
    cliente = db.query(Cliente).filter(Cliente.cpf == cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente_to_out(cliente)


@app.get("/sql/clientes", response_model=List[ClienteOut])
def listar_clientes(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    cidade: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lista clientes com paginação simples e filtros opcionais.
    Muito parecido com a versão Mongo, mas usando SQL/ORM.
    """
    query = db.query(Cliente)

    if status:
        if status not in ("ativo", "inativo"):
            raise HTTPException(
                status_code=400,
                detail="Status inválido. Use 'ativo' ou 'inativo'.",
            )
        query = query.filter(Cliente.status == status)

    if cidade:
        # endereco é JSON, então usamos JSON query dependendo do dialeto.
        # Exemplo simplificado: assumindo que o driver suporta ->> para JSON.
        from sqlalchemy import text
        query = query.filter(
            text("endereco->>'cidade' = :cidade")
        ).params(cidade=cidade)

    query = query.offset(max(skip, 0)).limit(min(max(limit, 1), 100))

    clientes = query.all()
    return [cliente_to_out(c) for c in clientes]


@app.post("/sql/clientes", response_model=ClienteOut, status_code=201)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """
    Cria um novo cliente no PostgreSQL.
    """
    # Verifica duplicidade de CPF
    existente = db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first()
    if existente:
        raise HTTPException(
            status_code=409,
            detail="Já existe um cliente cadastrado com esse CPF.",
        )

    model = Cliente(
        cpf=cliente.cpf,
        nome=cliente.nome,
        email=cliente.email,
        telefone=cliente.telefone,
        status=cliente.status,
        endereco=cliente.endereco.model_dump(),
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    return cliente_to_out(model)


@app.patch("/sql/clientes/{cpf}", response_model=ClienteOut)
def atualizar_cliente(cpf: str, atualizacao: ClienteUpdate, db: Session = Depends(get_db)):
    """
    Atualiza parcialmente um cliente no PostgreSQL, identificado pelo CPF.
    """
    cliente = db.query(Cliente).filter(Cliente.cpf == cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    data = atualizacao.model_dump(exclude_unset=True)

    if "endereco" in data and data["endereco"] is not None:
        data["endereco"] = data["endereco"].model_dump()

    for campo, valor in data.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)

    return cliente_to_out(cliente)


@app.delete("/sql/clientes/{cpf}", status_code=204)
def deletar_cliente(cpf: str, db: Session = Depends(get_db)):
    """
    Remove fisicamente um cliente da tabela (delete de verdade).
    Em produção, você poderia optar por um 'soft delete' similar ao do Mongo.
    """
    cliente = db.query(Cliente).filter(Cliente.cpf == cpf).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    db.delete(cliente)
    db.commit()

    return Response(status_code=204)
