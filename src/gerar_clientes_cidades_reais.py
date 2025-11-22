from datetime import datetime
import random

from faker import Faker
from pymongo.errors import DuplicateKeyError

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import get_collection

fake = Faker("pt_BR")

# Cidades reais por UF (capitais + algumas cidades grandes / turísticas)
CIDADES_POR_UF = {
    "AC": ["Rio Branco", "Cruzeiro do Sul"],
    "AL": ["Maceió", "Arapiraca"],
    "AP": ["Macapá", "Santana"],
    "AM": ["Manaus", "Parintins"],
    "BA": ["Salvador", "Feira de Santana", "Vitória da Conquista", "Porto Seguro"],
    "CE": ["Fortaleza", "Juazeiro do Norte", "Sobral"],
    "DF": ["Brasília"],
    "ES": ["Vitória", "Vila Velha", "Serra"],
    "GO": ["Goiânia", "Anápolis", "Aparecida de Goiânia"],
    "MA": ["São Luís", "Imperatriz"],
    "MT": ["Cuiabá", "Rondonópolis"],
    "MS": ["Campo Grande", "Dourados"],
    "MG": ["Belo Horizonte", "Uberlândia", "Juiz de Fora", "Contagem"],
    "PA": ["Belém", "Santarém", "Ananindeua"],
    "PB": ["João Pessoa", "Campina Grande"],
    "PR": ["Curitiba", "Londrina", "Maringá", "Foz do Iguaçu"],
    "PE": ["Recife", "Olinda", "Caruaru", "Petrolina"],
    "PI": ["Teresina", "Parnaíba"],
    "RJ": ["Rio de Janeiro", "Niterói", "Petrópolis", "Campos dos Goytacazes"],
    "RN": ["Natal", "Mossoró"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Gramado"],
    "RO": ["Porto Velho", "Ji-Paraná"],
    "RR": ["Boa Vista"],
    "SC": ["Florianópolis", "Joinville", "Blumenau", "Chapecó"],
    "SP": ["São Paulo", "Campinas", "Santos", "São José dos Campos", "Ribeirão Preto"],
    "SE": ["Aracaju", "Nossa Senhora do Socorro"],
    "TO": ["Palmas", "Araguaína"],
}

# Ajuste esses números se quiser MUITO mais ou menos clientes
TOTAL_CAPITAL = 3000      # por capital (primeira cidade da lista)
TOTAL_OUTRAS = 1000       # por cidade não capital

def gerar_cliente(cidade: str, uf: str) -> dict:
    """Gera um documento de cliente compatível com o restante do sistema."""
    nome = fake.name()
    cpf = fake.cpf()
    email = fake.email()
    telefone = fake.phone_number()

    data_nascimento = fake.date_of_birth(
        minimum_age=18,
        maximum_age=90
    ).strftime("%d/%m/%Y")

    endereco = {
        "rua": fake.street_name(),
        "numero": str(random.randint(1, 9999)),
        "complemento": "",  # complemento em branco (Faker pt_BR não tem secondary_address)
        "bairro": fake.bairro() if hasattr(fake, "bairro") else fake.city_suffix(),
        "cidade": cidade,
        "estado": uf,   # pode ser maiúsculo, a busca normaliza
        "cep": fake.postcode(),
    }

    return {
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "telefone": telefone,
        "data_nascimento": data_nascimento,
        "endereco": endereco,
        "status": "ativo",
        "data_cadastro": datetime.utcnow(),
    }

def main():
    col = get_collection()
    criados = 0
    erros = 0

    for uf, cidades in CIDADES_POR_UF.items():
        for idx, cidade in enumerate(cidades):
            alvo = TOTAL_CAPITAL if idx == 0 else TOTAL_OUTRAS
            print(f"Gerando {alvo} clientes para {cidade} - {uf}...")
            for _ in range(alvo):
                doc = gerar_cliente(cidade, uf)
                try:
                    col.insert_one(doc)
                    criados += 1
                except DuplicateKeyError:
                    # CPF ou e-mail duplicado: pula
                    erros += 1

    print("\n================ RESULTADO ================")
    print(f"✓ Clientes criados com sucesso: {criados}")
    print(f"✗ Erros (duplicados etc.): {erros}")
    print("==========================================")

if __name__ == "__main__":
    main()
