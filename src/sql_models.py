"""
Models (tabelas) SQLAlchemy para o PostgreSQL.

Aqui definimos a tabela Cliente, equivalente ao documento de cliente
que você tem no Mongo, mas em formato relacional.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    func,
)

from .sql_db import Base


class Cliente(Base):
    __tablename__ = "clientes_sql"  # nome da tabela no PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefone = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="ativo")
    endereco = Column(JSON, nullable=False)  # guardamos o endereço como JSON
    data_cadastro = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Cliente id={self.id} cpf={self.cpf} nome={self.nome!r}>"
