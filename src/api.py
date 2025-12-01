from typing import List, Optional
from pymongo.collection import ReturnDocument
import pandas as pd
from datetime import date
from scripts.analise_clientes_pandas import carregar_clientes_dataframe
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
    data_nascimento: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de nascimento no formato YYYY-MM-DD",
    )
    endereco: Endereco


class ClienteCreate(ClienteBase):
    cpf: str = Field(..., min_length=11, max_length=11)


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ativo|inativo)$")
    data_nascimento: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de nascimento no formato YYYY-MM-DD",
    )
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

@app.get("/relatorios/faixa-etaria")
def relatorio_faixa_etaria():
    """
    Retorna a distribuição de clientes por faixa etária,
    usando a coluna data_nascimento dos clientes do MongoDB.
    """
    df = carregar_clientes_dataframe()

    # Garante que data_nascimento é datetime do Pandas
    df["data_nascimento"] = pd.to_datetime(df["data_nascimento"], errors="coerce")

    # Remove linhas sem data_nascimento válida (NaT)
    df = df.dropna(subset=["data_nascimento"])

    # Usa um Timestamp do Pandas como "hoje"
    hoje = pd.Timestamp(date.today())

    # Calcula idade em anos (aprox.)
    df["idade"] = ((hoje - df["data_nascimento"]).dt.days / 365.25).astype("float")

        # Mantém só quem tem idade válida (não nula, não NaN)
    df_validos = df[df["idade"].notna()]

    if df_validos.empty:
            return {
                "mensagem": "Nenhum cliente com data_nascimento válida.",
                "total_clientes": 0,
                "faixas": [],
            }

    # Define as faixas etárias (mesma ideia dos relatórios em Pandas)
    bins = [0, 18, 26, 36, 51, 66, 200]
    labels = ["0-17", "18-25", "26-35", "36-50", "51-65", "66+"]

    df_validos["faixa_etaria"] = pd.cut(
        df_validos["idade"],
        bins=bins,
        labels=labels,
        right=False,
    )

    # Contagem por faixa
    tabela = (
        df_validos["faixa_etaria"]
        .value_counts()
        .sort_index()
        .rename_axis("faixa_etaria")
        .reset_index(name="quantidade")
    )

    total = int(tabela["quantidade"].sum())
    tabela["percentual"] = (tabela["quantidade"] / total * 100).round(2)

    # Monta resposta em formato JSON
    faixas = tabela.to_dict(orient="records")

    return {
        "mensagem": "Distribuição por faixa etária calculada com sucesso.",
        "total_clientes": total,
        "faixas": faixas,
    }


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
def atualizar_cliente(cpf: str, dados: ClienteUpdate):
    """Atualiza parcialmente um cliente pelo CPF (patch)."""

    # Monta só os campos que o usuário enviou
    campos_para_atualizar = dados.model_dump(exclude_unset=True)

    if not campos_para_atualizar:
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado enviado para atualização."
        )

    # Faz o update e já pede o documento atualizado de volta
    doc_atualizado = _collection.find_one_and_update(
        {"cpf": cpf},
        {"$set": campos_para_atualizar},
        return_document=ReturnDocument.AFTER,
    )

    if not doc_atualizado:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # 🔴 IMPORTANTE: converter do formato Mongo para o formato da API
    # (id como string, não expor _id bruto)
    return {
        "id": str(doc_atualizado["_id"]),
        "cpf": doc_atualizado["cpf"],
        "nome": doc_atualizado["nome"],
        "email": doc_atualizado.get("email"),
        "telefone": doc_atualizado.get("telefone"),
        "status": doc_atualizado.get("status"),
        "endereco": doc_atualizado.get("endereco"),
        "data_nascimento": doc_atualizado.get("data_nascimento"),
    }


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
