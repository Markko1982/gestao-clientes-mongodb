from datetime import datetime
from typing import Optional

class Cliente:
    """
    Modelo de dados para Cliente
    Representa um cliente da empresa com todas as informações necessárias
    """
    
    def __init__(self, 
                 nome: str,
                 cpf: str,
                 email: str,
                 telefone: str,
                 data_nascimento: str,
                 endereco: dict,
                 status: str = "ativo",
                 data_cadastro: Optional[datetime] = None,
                 _id: Optional[str] = None):
        """
        Inicializa um cliente
        
        Args:
            nome: Nome completo do cliente
            cpf: CPF (apenas números)
            email: Email do cliente
            telefone: Telefone com DDD
            data_nascimento: Data no formato YYYY-MM-DD
            endereco: Dicionário com rua, numero, bairro, cidade, estado, cep
            status: Status do cliente (ativo, inativo, bloqueado)
            data_cadastro: Data de cadastro (gerada automaticamente se não informada)
            _id: ID do MongoDB (gerado automaticamente)
        """
        self._id = _id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self.endereco = endereco
        self.status = status
        self.data_cadastro = data_cadastro or datetime.now()
    
    def to_dict(self) -> dict:
        """
        Converte o objeto Cliente para dicionário (formato MongoDB)
        
        Returns:
            Dicionário com todos os dados do cliente
        """
        cliente_dict = {
            "nome": self.nome,
            "cpf": self.cpf,
            "email": self.email,
            "telefone": self.telefone,
            "data_nascimento": self.data_nascimento,
            "endereco": self.endereco,
            "status": self.status,
            "data_cadastro": self.data_cadastro
        }
        
        if self._id:
            cliente_dict["_id"] = self._id
            
        return cliente_dict
    
    @staticmethod
    def from_dict(data: dict) -> 'Cliente':
        """
        Cria um objeto Cliente a partir de um dicionário (do MongoDB)
        
        Args:
            data: Dicionário com dados do cliente
            
        Returns:
            Objeto Cliente
        """
        return Cliente(
            _id=data.get("_id"),
            nome=data.get("nome"),
            cpf=data.get("cpf"),
            email=data.get("email"),
            telefone=data.get("telefone"),
            data_nascimento=data.get("data_nascimento"),
            endereco=data.get("endereco"),
            status=data.get("status", "ativo"),
            data_cadastro=data.get("data_cadastro")
        )
    
    def __str__(self) -> str:
        """Representação em string do cliente"""
        return f"Cliente: {self.nome} | CPF: {self.cpf} | Status: {self.status}"
