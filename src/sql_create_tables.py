"""
Cria as tabelas definidas em sql_models.py no banco PostgreSQL.

Equivalente a "subir o schema" do lado SQL.
"""

from .sql_db import engine, Base
from .sql_models import Cliente  # importa para registrar o model na Base


def main():
    print("Criando tabelas no PostgreSQL usando SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas (se já existiam, nada foi alterado).")


if __name__ == "__main__":
    main()
