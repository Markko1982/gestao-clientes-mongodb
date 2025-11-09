# 🏢 Sistema de Gestão de Clientes - MongoDB

Sistema completo de gerenciamento de clientes desenvolvido com Python, MongoDB e Docker. Projeto profissional com mais de 100 mil registros para simulação de ambiente de produção.

## 🚀 Tecnologias Utilizadas

- **Python 3.11** - Linguagem principal
- **MongoDB 7.0** - Banco de dados NoSQL
- **Docker** - Containerização do banco de dados
- **PyMongo** - Driver oficial MongoDB para Python
- **Faker** - Geração de dados fictícios realistas

## 📋 Funcionalidades

### CRUD Completo
- ✅ Criar novos clientes
- ✅ Buscar por CPF ou nome
- ✅ Atualizar dados (email, telefone, endereço, status)
- ✅ Listar clientes (com filtros)
- ✅ Inativar clientes (exclusão lógica)
- ✅ Deletar clientes (exclusão física)

### Relatórios e Análises
- 📊 Relatório de clientes por cidade (exportação CSV)
- 📈 Estatísticas gerais do sistema
- 🎯 Análise de distribuição geográfica
- 📉 Relatórios de clientes ativos/inativos

### Gerador de Dados
- 🎲 Geração automática de clientes fictícios
- 🇧🇷 Dados brasileiros realistas (nomes, CPFs, endereços)
- ⚡ Capaz de gerar milhares de registros rapidamente

## 🛠️ Instalação e Configuração

### Pré-requisitos
```bash
- Docker instalado
- Python 3.11+
- Git

1. Clonar o repositório

git clone https://github.com/Markko1982/gestao-clientes-mongodb.git
cd gestao-clientes-mongodb

2. Iniciar MongoDB com Docker

docker run -d --name mongodb-dev -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  mongo:latest

3. Criar ambiente virtual Python

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

4. Instalar dependências

pip install -r requirements.txt

5. Gerar dados fictícios (opcional )

python src/gerar_dados.py


🎮 Como Usar

Menu Principal

python src/menu_principal.py

Gerar Relatório de Cidades

python src/relatorio_cidades.py


Atalhos (Linux)

# Adicionar aliases ao ~/.bashrc
alias sistema-clientes='cd /dados/projetos/gestao-clientes-mongodb && source venv/bin/activate && python src/menu_principal.py'
alias gerar-clientes='cd /dados/projetos/gestao-clientes-mongodb && source venv/bin/activate && python src/gerar_dados.py'


📊 Estrutura do Projeto

gestao-clientes-mongodb/
├── src/
│   ├── cliente_model.py          # Modelo de dados
│   ├── cliente_crud.py            # Operações CRUD
│   ├── conexao.py                 # Teste de conexão
│   ├── gerar_dados.py             # Gerador de dados fictícios
│   ├── menu_principal.py          # Interface do sistema
│   └── relatorio_cidades.py       # Relatório por cidade
├── venv/                          # Ambiente virtual (não versionado)
├── .gitignore                     # Arquivos ignorados pelo Git
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo



💾 Modelo de Dados

Cliente {
    _id: ObjectId,
    nome: String,
    cpf: String (único),
    email: String,
    telefone: String,
    data_nascimento: String (YYYY-MM-DD),
    endereco: {
        rua: String,
        numero: String,
        complemento: String,
        bairro: String,
        cidade: String,
        estado: String,
        cep: String
    },
    status: String (ativo/inativo),
    data_cadastro: DateTime
}


📈 Estatísticas do Projeto
101.494 clientes cadastrados
42.315 cidades diferentes
27 estados brasileiros
90% clientes ativos
10% clientes inativos


🤝 Contribuindo
Contribuições são bem-vindas! Sinta-se à vontade para:
Fazer fork do projeto
Criar uma branch para sua feature (git checkout -b feature/NovaFuncionalidade)
Commit suas mudanças (git commit -m 'feat: Adiciona nova funcionalidade')
Push para a branch (git push origin feature/NovaFuncionalidade)
Abrir um Pull Request

📝 Licença
Este projeto é de código aberto e está disponível para uso educacional e comercial.

👤 Autor
Markko1982
GitHub: @Markko1982
⭐ Se este projeto foi útil para você, considere dar uma estrela!

