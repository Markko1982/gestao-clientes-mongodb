from typing import List, Optional
from pymongo.collection import ReturnDocument
import pandas as pd
from datetime import date
from scripts.analise_clientes_pandas import carregar_clientes_dataframe
from fastapi import FastAPI, HTTPException, Response, Query, Request
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.exception_handlers import request_validation_exception_handler



from config import get_collection
from logging_config import get_logger



# Obter conexão com MongoDB (um único client para toda a API)
_bundle = get_collection()
_client = _bundle.client
_db = _bundle.db
_collection = _bundle.collection
logger = get_logger(__name__)



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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Payload inválido para criação de cliente.",
            "errors": exc.errors(),
        },
    )



@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logar todas as requisições HTTP em formato estruturado.
    """
    import time

    start = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        status_code = getattr(response, "status_code", None)

        logger.info(
            "HTTP request",
            extra={
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "client_ip": request.client.host if request.client else None,
                "duration_ms": round(duration_ms, 2),
            },
        )


@app.get("/health")
def health_check():
    """Endpoint simples para verificar se a API e o Mongo estão OK."""
    try:
        # Verifica se o MongoDB está respondendo
        _db.command("ping")

        # Conta clientes não marcados para exclusão (ajuste se o seu filtro for outro)
        total = _collection.count_documents({"marcado_para_exclusao": {"$ne": True}})

        # Log de sucesso estruturado
        logger.info(
            "health_check OK",
            extra={
                "event": "health_ok",
                "database": _db.name,
                "collection": _collection.name,
                "total_clientes": total,
            },
        )

        return {
            "status": "ok",
            "database": _db.name,
            "collection": _collection.name,
            "total_clientes": total,
        }
    except Exception as e:
        # Log de erro com stacktrace
        logger.exception(
            "health_check FAILED",
            extra={"event": "health_error"},
        )
        # Aqui você decide se quer expor o erro ou não;
        # por enquanto vamos devolver a mensagem para facilitar debug.
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clientes/{cpf}", response_model=ClienteOut)
def obter_cliente_por_cpf(cpf: str):
    """Obtém um cliente pelo CPF."""
    doc = _collection.find_one({"cpf": cpf})

    if not doc:
        # Log estruturado quando não encontra o cliente
        logger.warning(
            f"cliente_get_not_found cpf={cpf}",
            extra={"event": "cliente_get_not_found"},
        )
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado.",
        )

    # Log estruturado de sucesso na busca
    logger.info(
        f"cliente_get_success cpf={cpf}",
        extra={"event": "cliente_get_success"},
    )
    return _doc_to_cliente_out(doc)


@app.get("/clientes", response_model=List[ClienteOut])
def listar_clientes(
    status: Optional[str] = Query(
        None,
        pattern="^(ativo|inativo)$",
        description="Filtrar por status do cliente (ativo ou inativo).",
    ),
    estado: Optional[str] = Query(
        None,
        min_length=2,
        max_length=2,
        description="Filtrar por estado (UF), ex: SP, RJ.",
    ),
    cidade: Optional[str] = Query(
        None,
        description="Filtrar por cidade (nome completo ou parcial).",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=200,
        description="Quantidade máxima de clientes a retornar (1-200).",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Quantidade de clientes a pular (para paginação).",
    ),
):
    # Filtro base: ignorar clientes marcados para exclusão (se esse campo existir)
    filtro: dict = {"marcado_para_exclusao": {"$ne": True}}

    if status:
        filtro["status"] = status

    if estado:
        filtro["endereco.estado"] = estado.strip().upper()

    if cidade:
        filtro["endereco.cidade"] = {
            "$regex": cidade.strip(),
            "$options": "i",  # case-insensitive
        }

    cursor = (
        _collection.find(filtro)
        .sort("nome", 1)   # ordena por nome ascendente
        .skip(offset)      # paginação: pula 'offset' registros
        .limit(limit)      # pega no máximo 'limit' registros
    )

    # Aproveitar o helper que você já tem (_doc_to_cliente_out)
    clientes: List[ClienteOut] = [
        _doc_to_cliente_out(doc) for doc in cursor
    ]

    return clientes


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

    @app.get("/relatorios/cidades-mais-inativos")
    def relatorio_cidades_mais_inativos(limite: int = 10):
        """
        Retorna as top N cidades com maior número de clientes inativos,
        usando os dados carregados do MongoDB via Pandas.
        """
        # Limite de segurança para não devolver uma lista gigante
        if limite <= 0 or limite > 100:
            raise HTTPException(
                status_code=400,
                detail="Parâmetro 'limite' deve estar entre 1 e 100.",
            )

        # Carrega todos os clientes (ignorando marcados para exclusão)
        df = carregar_clientes_dataframe()

        if "status" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="DataFrame não possui coluna 'status'.",
            )

        # Filtra apenas clientes inativos
        df_inativos = df[df["status"] == "inativo"].copy()

        # Caso não haja nenhum inativo, retorna resposta vazia, mas estruturada
        if df_inativos.empty:
            return {
                "mensagem": "Nenhum cliente inativo encontrado.",
                "total_inativos": 0,
                "limite": limite,
                "cidades": [],
            }

        # Normaliza campos de cidade/estado para evitar valores NaN
        df_inativos["estado"] = df_inativos["estado"].fillna("(sem estado)")
        df_inativos["cidade"] = df_inativos["cidade"].fillna("(sem cidade)")

        # Agrupa por estado + cidade e conta quantos inativos há em cada combinação
        agrupado = (
            df_inativos
            .groupby(["estado", "cidade"])
            .size()
            .reset_index(name="quantidade_inativos")
            .sort_values(by="quantidade_inativos", ascending=False)
        )

        # Total de clientes inativos (para cálculo de percentual)
        total_inativos = int(df_inativos.shape[0])

        # Percentual de inativos daquela cidade em relação ao total de inativos
        agrupado["percentual"] = (
            agrupado["quantidade_inativos"] / total_inativos * 100
        ).round(2)

        # Aplica o limite e converte para lista de dicts
        top_cidades = agrupado.head(limite).to_dict(orient="records")

        return {
            "mensagem": "Top cidades com mais clientes inativos calculado com sucesso.",
            "total_inativos": total_inativos,
            "limite": limite,
            "cidades": top_cidades,
        }


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

@app.get("/relatorios/dominios-email")
async def relatorio_dominios_email():
    """
    Retorna o top 10 de domínios de e-mail dos clientes,
    com quantidade e percentual em relação ao total de e-mails válidos.
    """
    # Carrega todos os clientes em um DataFrame (reutilizando a função de scripts)
    df = carregar_clientes_dataframe().copy()

    # Garante que a coluna de e-mail existe (por segurança)
    if "email" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="Coluna 'email' não encontrada no DataFrame de clientes."
        )

    # Limpa e-mails vazios ou nulos
    df["email"] = df["email"].fillna("").str.strip()
    df = df[df["email"] != ""]

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="Nenhum cliente com e-mail definido."
        )

    # Extrai o domínio do e-mail (parte depois do @)
    df["dominio_email"] = (
        df["email"]
        .str.split("@").str[-1]
        .str.lower()
        .str.strip()
    )

    # Conta quantos clientes por domínio
    contagem_dominios = df["dominio_email"].value_counts()

    total_com_email = int(contagem_dominios.sum())
    top10 = contagem_dominios.head(10)

    # Monta a resposta em forma de lista de dicts
    top_dominios = []
    for dominio, quantidade in top10.items():
        percentual = round(quantidade / total_com_email * 100, 2)
        top_dominios.append(
            {
                "dominio": dominio,
                "quantidade": int(quantidade),
                "percentual": percentual,
            }
        )

    return {
        "mensagem": "Top domínios de e-mail calculado com sucesso.",
        "total_clientes_com_email": total_com_email,
        "top_dominios": top_dominios,
    }

@app.get("/relatorios/cidades-inativos")
async def relatorio_cidades_inativos(
    min_clientes: int = 50,
    limite: int = 20,
):
    """
    Retorna as cidades com maior percentual de clientes inativos.

    - min_clientes: número mínimo de clientes por cidade para entrar no ranking.
    - limite: quantidade de cidades no resultado (default: top 20).
    """
    # Carrega os clientes em DataFrame
    df = carregar_clientes_dataframe().copy()

    # Garante colunas necessárias
    colunas_necessarias = {"status", "estado", "cidade"}
    if not colunas_necessarias.issubset(df.columns):
        raise HTTPException(
            status_code=500,
            detail=f"Colunas necessárias não encontradas no DataFrame: {colunas_necessarias}",
        )

    # Preenche valores nulos
    df["status"] = df["status"].fillna("desconhecido")
    df["estado"] = df["estado"].fillna("(sem estado)")
    df["cidade"] = df["cidade"].fillna("(sem cidade)")

    # Tabela status por cidade/estado
    tabela_cidade_status = (
        df.groupby(["estado", "cidade", "status"])
        .size()
        .unstack(fill_value=0)
    )

    # Garante colunas 'ativo' e 'inativo' existindo
    if "ativo" not in tabela_cidade_status.columns:
        tabela_cidade_status["ativo"] = 0
    if "inativo" not in tabela_cidade_status.columns:
        tabela_cidade_status["inativo"] = 0

    # Total por cidade e quantidade de inativos
    tabela_cidade_status["total"] = (
        tabela_cidade_status["ativo"] + tabela_cidade_status["inativo"]
    )

    # Filtra por mínimo de clientes
    tabela_filtrada = tabela_cidade_status[
        tabela_cidade_status["total"] >= min_clientes
    ].copy()

    if tabela_filtrada.empty:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma cidade com quantidade mínima de clientes para o relatório.",
        )

    # Percentual de inativos
    tabela_filtrada["perc_inativos"] = (
        tabela_filtrada["inativo"] / tabela_filtrada["total"] * 100
    ).round(2)

    # Ordena por percentual de inativos (desc) e pega top N
    top_cidades = (
        tabela_filtrada.sort_values(
            by="perc_inativos",
            ascending=False,
        )
        .head(limite)
        .reset_index()
    )

    # Monta a resposta
    cidades = []
    for _, row in top_cidades.iterrows():
        cidades.append(
            {
                "estado": row["estado"],
                "cidade": row["cidade"],
                "inativo": int(row["inativo"]),
                "total": int(row["total"]),
                "perc_inativos": float(row["perc_inativos"]),
            }
        )

    return {
        "mensagem": "Ranking de cidades por percentual de inativos calculado com sucesso.",
        "min_clientes": int(min_clientes),
        "limite": int(limite),
        "total_cidades_no_ranking": len(cidades),
        "cidades": cidades,
    }
@app.get("/relatorios/status-por-estado")
async def relatorio_status_por_estado(min_clientes: int = 0):
    """
    Retorna, por estado (UF), a quantidade de clientes ativos/inativos,
    total e percentual em cada status.

    - min_clientes: se > 0, só retorna estados com pelo menos essa quantidade de clientes.
    """
    df = carregar_clientes_dataframe().copy()

    # Garante as colunas necessárias
    colunas_necessarias = {"status", "estado"}
    if not colunas_necessarias.issubset(df.columns):
        raise HTTPException(
            status_code=500,
            detail=f"Colunas necessárias não encontradas: {colunas_necessarias}",
        )

    # Limpa dados
    df["status"] = df["status"].fillna("desconhecido").str.strip().str.lower()
    df["estado"] = df["estado"].fillna("(sem estado)").str.strip().str.upper()

    # Agrupa por estado e status
    tabela = (
        df.groupby(["estado", "status"])
        .size()
        .unstack(fill_value=0)
    )

    # Garante as colunas padrão
    if "ativo" not in tabela.columns:
        tabela["ativo"] = 0
    if "inativo" not in tabela.columns:
        tabela["inativo"] = 0

    # Total por estado
    tabela["total"] = tabela["ativo"] + tabela["inativo"]

    # Aplica filtro de mínimo de clientes, se informado
    if min_clientes > 0:
        tabela = tabela[tabela["total"] >= min_clientes]

    if tabela.empty:
        raise HTTPException(
            status_code=404,
            detail="Nenhum estado com clientes para o critério informado.",
        )

    # Percentuais dentro de cada estado
    tabela["perc_ativos"] = (tabela["ativo"] / tabela["total"] * 100).round(2)
    tabela["perc_inativos"] = (tabela["inativo"] / tabela["total"] * 100).round(2)

    # Ordena por total de clientes (maior primeiro)
    tabela = tabela.sort_values(by="total", ascending=False).reset_index()

    # Monta resposta
    estados = []
    for _, row in tabela.iterrows():
        estados.append(
            {
                "estado": row["estado"],
                "ativo": int(row["ativo"]),
                "inativo": int(row["inativo"]),
                "total": int(row["total"]),
                "perc_ativos": float(row["perc_ativos"]),
                "perc_inativos": float(row["perc_inativos"]),
            }
        )

    total_geral = int(df.shape[0])

    return {
        "mensagem": "Status de clientes por estado calculado com sucesso.",
        "total_geral_clientes": total_geral,
        "min_clientes": int(min_clientes),
        "total_estados_no_relatorio": len(estados),
        "estados": estados,
    }


@app.post("/clientes", response_model=ClienteOut, status_code=201)
def criar_cliente(cliente: ClienteCreate):
    """Cria um novo cliente. CPF deve ser único."""
    data = cliente.model_dump()
    # endereço vem como Endereco → convertemos para dict bruto
    data["endereco"] = cliente.endereco.model_dump()

    try:
        result = _collection.insert_one(data)

        # Log de sucesso da criação do cliente
        logger.info(
            f"cliente_create_success cpf={cliente.cpf} status={data.get('status')}",
            extra={
                "event": "cliente_create_success",
            },
        )
    except DuplicateKeyError:
        # Log estruturado do conflito de CPF duplicado
        logger.warning(
            f"cliente_create_conflict cpf={cliente.cpf}",
            extra={
                "event": "cliente_create_conflict",
            },
        )
        raise HTTPException(
            status_code=409,
            detail="Já existe um cliente cadastrado com esse CPF.",
        )

    doc = _collection.find_one({"_id": result.inserted_id})
    return _doc_to_cliente_out(doc)


@app.patch("/clientes/{cpf}", response_model=ClienteOut)
def atualizar_cliente(cpf: str, cliente_update: ClienteUpdate):
    """Atualiza parcialmente um cliente pelo CPF."""
    # Monta apenas os campos enviados no corpo da requisição
    update_data = cliente_update.model_dump(exclude_unset=True)

    if not update_data:
        # Nada foi enviado para atualizar
        logger.info(
            f"cliente_update_no_fields cpf={cpf}",
            extra={"event": "cliente_update_no_fields"},
        )
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado enviado para atualização.",
        )

    # Executa o update e já retorna o documento atualizado
    updated_doc = _collection.find_one_and_update(
        {"cpf": cpf},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )

    if not updated_doc:
        # CPF não encontrado
        logger.warning(
            f"cliente_update_not_found cpf={cpf}",
            extra={"event": "cliente_update_not_found"},
        )
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado.",
        )

    # Sucesso na atualização
    logger.info(
        f"cliente_update_success cpf={cpf}",
        extra={"event": "cliente_update_success"},
    )

    return _doc_to_cliente_out(updated_doc)




@app.delete("/clientes/{cpf}", status_code=204)
def deletar_cliente(cpf: str):
    """Remove um cliente pelo CPF."""
    result = _collection.delete_one({"cpf": cpf})

    if result.deleted_count == 0:
        # Log estruturado quando não encontra o cliente para deletar
        logger.warning(
            f"cliente_delete_not_found cpf={cpf}",
            extra={"event": "cliente_delete_not_found"},
        )
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado.",
        )

    # Log estruturado de sucesso na remoção
    logger.info(
        f"cliente_delete_success cpf={cpf}",
        extra={"event": "cliente_delete_success"},
    )
    # Para status_code=204, podemos simplesmente não retornar corpo
    return

@app.on_event("shutdown")
def fechar_conexao_mongo():
    """Garante que o client do Mongo seja fechado ao desligar a API."""
    _client.close()
