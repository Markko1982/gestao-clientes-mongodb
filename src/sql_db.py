"""
Configuração básica do SQLAlchemy para PostgreSQL.

Este arquivo é o equivalente "SQL" do que o config.py faz para o Mongo:
- define DATABASE_URL;
- cria o engine do SQLAlchemy;
- cria a SessionLocal (sessões de conexão);
- expõe a Base (para declarar models);
- expõe uma dependência get_db() para usar na API FastAPI.

ATENÇÃO:
- Ajuste a DATABASE_URL para o seu ambiente real de PostgreSQL.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# URL de exemplo para um PostgreSQL local.
# Ajuste USUÁRIO, SENHA, HOST, PORTA e NOME_BANCO conforme o seu ambiente.
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/clientes_db"

# Cria o engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,  # mude para True se quiser ver as queries no console
)

# Fábrica de sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# Classe base para os models (tabelas)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependência para FastAPI: abre uma sessão para cada requisição e
    garante o fechamento no final.
    """
    db = S
