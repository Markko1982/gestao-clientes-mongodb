from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from typing import List, Optional
from cliente_model import Cliente
from datetime import datetime

class ClienteCRUD:
    """
    Classe responsável pelas operações CRUD de clientes no MongoDB
    CRUD = Create (Criar), Read (Ler), Update (Atualizar), Delete (Deletar)
    """
    
    def __init__(self, uri: str = "mongodb://admin:admin123@localhost:27017/"):
        """
        Inicializa a conexão com MongoDB
        
        Args:
            uri: String de conexão do MongoDB
        """
        self.cliente_mongo = MongoClient(uri)
        self.db = self.cliente_mongo["empresa_db"]  # Nome do banco de dados
        self.colecao = self.db["clientes"]  # Nome da coleção (tabela)
        
        # Criar índice único no CPF para evitar duplicatas
        self.colecao.create_index("cpf", unique=True)
        print("✓ Conexão com MongoDB estabelecida")
    
    def criar_cliente(self, cliente: Cliente) -> bool:
        """
        Cria um novo cliente no banco de dados
        
        Args:
            cliente: Objeto Cliente a ser inserido
            
        Returns:
            True se sucesso, False se erro
        """
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
        Busca um cliente pelo CPF
        
        Args:
            cpf: CPF do cliente (apenas números)
            
        Returns:
            Objeto Cliente se encontrado, None caso contrário
        """
        try:
            resultado = self.colecao.find_one({"cpf": cpf})
            if resultado:
                return Cliente.from_dict(resultado)
            return None
        except Exception as e:
            print(f"✗ Erro ao buscar cliente: {e}")
            return None
    
    def buscar_por_nome(self, nome: str) -> List[Cliente]:
        """
        Busca clientes por nome (busca parcial, case-insensitive)
        
        Args:
            nome: Nome ou parte do nome do cliente
            
        Returns:
            Lista de objetos Cliente encontrados
        """
        try:
            # Regex para busca parcial e case-insensitive
            resultados = self.colecao.find({"nome": {"$regex": nome, "$options": "i"}})
            return [Cliente.from_dict(r) for r in resultados]
        except Exception as e:
            print(f"✗ Erro ao buscar clientes: {e}")
            return []
    
    def listar_todos(self, limite: int = 0) -> List[Cliente]:
        """
        Lista todos os clientes
        
        Args:
            limite: Número máximo de resultados (0 = sem limite)
            
        Returns:
            Lista de objetos Cliente
        """
        try:
            if limite > 0:
                resultados = self.colecao.find().limit(limite)
            else:
                resultados = self.colecao.find()
            return [Cliente.from_dict(r) for r in resultados]
        except Exception as e:
            print(f"✗ Erro ao listar clientes: {e}")
            return []
    
    def atualizar_cliente(self, cpf: str, novos_dados: dict) -> bool:
        """
        Atualiza dados de um cliente
        
        Args:
            cpf: CPF do cliente a ser atualizado
            novos_dados: Dicionário com os campos a serem atualizados
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            resultado = self.colecao.update_one(
                {"cpf": cpf},
                {"$set": novos_dados}
            )
            if resultado.matched_count > 0:
                print(f"✓ Cliente com CPF {cpf} atualizado com sucesso")
                return True
            else:
                print(f"✗ Cliente com CPF {cpf} não encontrado")
                return False
        except Exception as e:
            print(f"✗ Erro ao atualizar cliente: {e}")
            return False
    
    def deletar_cliente(self, cpf: str) -> bool:
        """
        Deleta um cliente do banco (exclusão física)
        
        Args:
            cpf: CPF do cliente a ser deletado
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            resultado = self.colecao.delete_one({"cpf": cpf})
            if resultado.deleted_count > 0:
                print(f"✓ Cliente com CPF {cpf} deletado com sucesso")
                return True
            else:
                print(f"✗ Cliente com CPF {cpf} não encontrado")
                return False
        except Exception as e:
            print(f"✗ Erro ao deletar cliente: {e}")
            return False
    
    def inativar_cliente(self, cpf: str) -> bool:
        """
        Inativa um cliente (exclusão lógica - mantém no banco mas marca como inativo)
        
        Args:
            cpf: CPF do cliente a ser inativado
            
        Returns:
            True se sucesso, False se erro
        """
        return self.atualizar_cliente(cpf, {"status": "inativo"})
    
    def contar_clientes(self, filtro: dict = {}) -> int:
        """
        Conta o número de clientes
        
        Args:
            filtro: Filtro opcional (ex: {"status": "ativo"})
            
        Returns:
            Número de clientes
        """
        try:
            return self.colecao.count_documents(filtro)
        except Exception as e:
            print(f"✗ Erro ao contar clientes: {e}")
            return 0
    
    def fechar_conexao(self):
        """Fecha a conexão com o MongoDB"""
        self.cliente_mongo.close()
        print("✓ Conexão com MongoDB fechada")
