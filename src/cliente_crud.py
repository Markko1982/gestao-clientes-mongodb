from typing import List, Optional
from pathlib import Path
import sys

# Ajuste de caminhos:
# - adiciona raiz do projeto (onde está config.py)
# - adiciona a pasta src (onde está cliente_model.py)
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

from cliente_model import Cliente  # src/cliente_model.py
from config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME  # type: ignore


class ClienteCRUD:
    """
    Classe responsável pelas operações CRUD de clientes no MongoDB.

    Todas as consultas padrão ignoram registros marcados como
    'marcado_para_exclusao = True' (soft delete de duplicados).
    """

    def __init__(self, uri: Optional[str] = None):
        """
        Inicializa a conexão com MongoDB.

        Args:
            uri: String de conexão do MongoDB; se None, usa MONGO_URI do config.py.
        """
        if uri is None:
            uri = MONGO_URI

        self.cliente_mongo = MongoClient(uri)
        self.db = self.cliente_mongo[MONGO_DB_NAME]
        self.colecao = self.db[MONGO_COLLECTION_NAME]

        # Índice único em CPF (idempotente)
        self.colecao.create_index("cpf", unique=True)
        print(
            f"✓ Conexão com MongoDB estabelecida "
            f"(db={self.db.name!r}, colecao={self.colecao.name!r})"
        )

    # ----------------- Helpers internos -----------------

    @staticmethod
    def _filtro_nao_excluido(filtro: Optional[dict] = None) -> dict:
        """
        Garante que o filtro inclua 'marcado_para_exclusao != True'.

        Usado em todas as consultas/listagens para esconder duplicados
        marcados para exclusão.
        """
        filtro_final = dict(filtro) if filtro else {}
        if "marcado_para_exclusao" not in filtro_final:
            filtro_final["marcado_para_exclusao"] = {"$ne": True}
        return filtro_final

    # ----------------- Operações CRUD -----------------

    def criar_cliente(self, cliente: Cliente) -> bool:
        """Insere um novo cliente na coleção."""
        try:
            resultado = self.colecao.insert_one(cliente.to_dict())
            print(f"✓ Cliente {cliente.nome} cadastrado com ID: {resultado.inserted_id}")
            return True
        except DuplicateKeyError:
            print(f"✗ Erro: CPF {cliente.cpf} já cadastrado!")
            return False
        except Exception as e:
            print(f"✗ Erro ao cadastrar cliente: {e}")
            return False

    def buscar_por_cpf(self, cpf: str) -> Optional[Cliente]:
        """
        Busca um cliente pelo CPF (apenas não marcados_para_exclusao).

        Returns:
            Cliente ou None.
        """
        try:
            filtro = self._filtro_nao_excluido({"cpf": cpf})
            resultado = self.colecao.find_one(filtro)
            if resultado:
                return Cliente.from_dict(resultado)
            return None
        except Exception as e:
            print(f"✗ Erro ao buscar cliente por CPF: {e}")
            return None

    def buscar_por_nome(self, nome: str) -> List[Cliente]:
        """
        Busca clientes por nome (parcial, case-insensitive), ignorando
        marcados_para_exclusao.
        """
        try:
            filtro_base = {"nome": {"$regex": nome, "$options": "i"}}
            filtro = self._filtro_nao_excluido(filtro_base)
            resultados = self.colecao.find(filtro)
            return [Cliente.from_dict(doc) for doc in resultados]
        except Exception as e:
            print(f"✗ Erro ao buscar clientes por nome: {e}")
            return []

    def listar_todos(self, limite: Optional[int] = None) -> List[Cliente]:
        """
        Lista todos os clientes não marcados_para_exclusao, ordenados por nome.

        Args:
            limite: número máximo de clientes a retornar (None ou <= 0 = todos).
        """
        try:
            filtro = self._filtro_nao_excluido()
            cursor = self.colecao.find(filtro).sort("nome", ASCENDING)
            if limite is not None and limite > 0:
                cursor = cursor.limit(limite)
            return [Cliente.from_dict(doc) for doc in cursor]
        except Exception as e:
            print(f"✗ Erro ao listar clientes: {e}")
            return []

    def deletar_por_cpf(self, cpf: str) -> bool:
        """
        Remove fisicamente um cliente pelo CPF.

        (Aqui NÃO aplicamos _filtro_nao_excluido de propósito:
         se o usuário pedir para excluir um CPF, removemos o registro
         correspondente, que é único pelo índice em cpf.)
        """
        try:
            resultado = self.colecao.delete_one({"cpf": cpf})
            if resultado.deleted_count > 0:
                print(f"✓ Cliente com CPF {cpf} removido com sucesso")
                return True
            else:
                print(f"✗ Cliente com CPF {cpf} não encontrado")
                return False
        except Exception as e:
            print(f"✗ Erro ao deletar cliente: {e}")
            return False

    def atualizar_cliente(self, cpf: str, novos_dados: dict) -> bool:
        """
        Atualiza dados de um cliente (apenas se NÃO estiver marcado_para_exclusao).
        """
        try:
            filtro = self._filtro_nao_excluido({"cpf": cpf})
            resultado = self.colecao.update_one(filtro, {"$set": novos_dados})
            if resultado.matched_count > 0:
                print(f"✓ Cliente com CPF {cpf} atualizado com sucesso")
                return True
            else:
                print(f"✗ Cliente com CPF {cpf} não encontrado ou marcado para exclusão")
                return False
        except Exception as e:
            print(f"✗ Erro ao atualizar cliente: {e}")
            return False

    def buscar_por_cidade(self, cidade: str) -> List[Cliente]:
        """
        Busca clientes por cidade (campo endereco.cidade),
        ignorando marcados_para_exclusao.
        """
        try:
            filtro_base = {"endereco.cidade": cidade}
            filtro = self._filtro_nao_excluido(filtro_base)
            resultados = self.colecao.find(filtro)
            return [Cliente.from_dict(doc) for doc in resultados]
        except Exception as e:
            print(f"✗ Erro ao buscar clientes por cidade: {e}")
            return []

    def buscar_por_status(self, status: str) -> List[Cliente]:
        """
        Busca clientes pelo status (ativo/inativo), ignorando duplicados marcados.
        """
        try:
            filtro_base = {"status": status}
            filtro = self._filtro_nao_excluido(filtro_base)
            resultados = self.colecao.find(filtro)
            return [Cliente.from_dict(doc) for doc in resultados]
        except Exception as e:
            print(f"✗ Erro ao buscar clientes por status: {e}")
            return []

    def contar_clientes(self, filtro: Optional[dict] = None) -> int:
        """
        Conta clientes considerando apenas registros não marcados_para_exclusao.
        """
        try:
            filtro_final = self._filtro_nao_excluido(filtro)
            return self.colecao.count_documents(filtro_final)
        except Exception as e:
            print(f"✗ Erro ao contar clientes: {e}")
            return 0

    def fechar_conexao(self):
        """Fecha a conexão com o MongoDB."""
        self.cliente_mongo.close()
        print("✓ Conexão com MongoDB fechada")

    def deletar_cliente(self, cpf: str) -> bool:
        """
        Compatibilidade com o menu principal.

        Deleta fisicamente um cliente pelo CPF, delegando para deletar_por_cpf.
        Retorna True se algum registro foi removido, False caso contrário.
        """
        return self.deletar_por_cpf(cpf)


    def inativar_cliente(self, cpf: str) -> bool:
        """
        Marca o cliente como inativo (status = 'inativo').

        Usa a lógica de atualizar_cliente para respeitar
        o filtro de 'marcado_para_exclusao'.
        """
        return self.atualizar_cliente(cpf, {"status": "inativo"})

