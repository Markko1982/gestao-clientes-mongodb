from faker import Faker
from cliente_model import Cliente
from cliente_crud import ClienteCRUD
from datetime import datetime, timedelta
import random

# Inicializar Faker com localização brasileira
fake = Faker('pt_BR')

def gerar_cpf_valido():
    """
    Gera um CPF válido (apenas números)
    
    Returns:
        String com 11 dígitos
    """
    # Gera 9 primeiros dígitos
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcula primeiro dígito verificador
    soma = sum([(10 - i) * cpf[i] for i in range(9)])
    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 > 9 else digito1
    cpf.append(digito1)
    
    # Calcula segundo dígito verificador
    soma = sum([(11 - i) * cpf[i] for i in range(10)])
    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 > 9 else digito2
    cpf.append(digito2)
    
    return ''.join(map(str, cpf))

def gerar_cliente_aleatorio() -> Cliente:
    """
    Gera um cliente com dados fictícios realistas
    
    Returns:
        Objeto Cliente com dados aleatórios
    """
    # Gerar data de nascimento entre 18 e 80 anos atrás
    anos_atras = random.randint(18, 80)
    data_nascimento = datetime.now() - timedelta(days=anos_atras * 365)
    
    # Gerar endereço completo
    endereco = {
        "rua": fake.street_name(),
        "numero": str(random.randint(1, 9999)),
        "complemento": random.choice(["", "Apto " + str(random.randint(1, 500)), "Casa", "Bloco " + str(random.randint(1, 10))]),
        "bairro": fake.bairro(),
        "cidade": fake.city(),
        "estado": fake.estado_sigla(),
        "cep": fake.postcode()
    }
    
    # Gerar telefone com DDD
    ddd = random.choice(['11', '21', '31', '41', '51', '61', '71', '81', '85', '91'])
    telefone = f"({ddd}) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
    
    # Status aleatório (90% ativo, 10% inativo)
    status = random.choices(["ativo", "inativo"], weights=[90, 10])[0]
    
    # Data de cadastro aleatória nos últimos 2 anos
    dias_atras = random.randint(1, 730)
    data_cadastro = datetime.now() - timedelta(days=dias_atras)
    
    # Criar cliente
    cliente = Cliente(
        nome=fake.name(),
        cpf=gerar_cpf_valido(),
        email=fake.email(),
        telefone=telefone,
        data_nascimento=data_nascimento.strftime("%Y-%m-%d"),
        endereco=endereco,
        status=status,
        data_cadastro=data_cadastro
    )
    
    return cliente

def popular_banco(quantidade: int = 1000):
    """
    Popula o banco de dados com clientes fictícios
    
    Args:
        quantidade: Número de clientes a serem gerados
    """
    print(f"\n{'='*60}")
    print(f"GERADOR DE DADOS FICTÍCIOS - SISTEMA DE CLIENTES")
    print(f"{'='*60}\n")
    
    # Conectar ao banco
    crud = ClienteCRUD()
    
    # Verificar quantos clientes já existem
    total_existente = crud.contar_clientes()
    print(f"📊 Clientes já cadastrados: {total_existente}")
    print(f"🎲 Gerando {quantidade} novos clientes fictícios...\n")
    
    sucesso = 0
    erro = 0
    
    for i in range(quantidade):
        try:
            cliente = gerar_cliente_aleatorio()
            if crud.criar_cliente(cliente):
                sucesso += 1
            else:
                erro += 1
            
            # Mostrar progresso a cada 100 clientes
            if (i + 1) % 100 == 0:
                print(f"Progresso: {i + 1}/{quantidade} clientes processados...")
                
        except Exception as e:
            erro += 1
            print(f"Erro ao gerar cliente {i + 1}: {e}")
    
    print(f"\n{'='*60}")
    print(f"RESULTADO:")
    print(f"✓ Clientes criados com sucesso: {sucesso}")
    print(f"✗ Erros (CPF duplicado ou outros): {erro}")
    print(f"📊 Total de clientes no banco: {crud.contar_clientes()}")
    print(f"{'='*60}\n")
    
    crud.fechar_conexao()

# Executar se o arquivo for rodado diretamente
if __name__ == "__main__":
    # Gerar 1500 clientes fictícios
    popular_banco(100000)
