# Sistema de Gestão de Clientes – MongoDB

Sistema completo de **gestão de clientes em linha de comando**, desenvolvido com **Python**, **MongoDB** e **Docker**.  
O projeto foi pensado tanto como **exercício prático** quanto como **projeto de portfólio**, simulando um ambiente real com **mais de 100 mil registros**.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.12** – Linguagem principal
- **MongoDB 7.x** – Banco de dados NoSQL
- **Docker / Docker Compose** – Sobe o MongoDB em contêiner
- **PyMongo** – Driver oficial MongoDB para Python
- **Faker** – Geração de dados fictícios realistas (nomes, CPFs, endereços brasileiros)

---

## ✅ Funcionalidades Principais

### CRUD Completo

- Criar novos clientes
- Buscar cliente por:
  - **CPF exato**
  - **Nome (contém)** – sem diferenciar maiúsculas/minúsculas ou acentos  
    (ex.: `florianopolis`, `Florianópolis`, `FLORIANOPOLIS` funcionam igual)
  - **Cidade e estado (UF)** – também ignorando acentos
- Atualizar dados do cliente:
  - E-mail
  - Telefone
  - Endereço completo (rua, número, complemento, bairro, cidade, estado, CEP)
  - Status (**ativo** / **inativo**)
- Inativar cliente (exclusão lógica)
- Deletar cliente (exclusão física)

### Listagem de Clientes

- Listar **todos** os clientes
- Listar apenas **ativos**
- Listar apenas **inativos**
- Definir **limite de resultados** (ex.: mostrar só os 20 primeiros)

### Relatórios e Análises

Todos os relatórios utilizam **agregações do MongoDB** e podem gerar arquivos **CSV** para análise em planilhas.

- **Relatório por faixa etária**  
  Agrupa clientes em faixas (menores de 18, 18–25, 26–35, 36–45, 46–60, acima de 60).
- **Relatório por cidade (TOP N + CSV)**  
  Mostra as cidades com mais clientes, percentual sobre o total e gera `dados/clientes_por_cidade.csv`.
- **Relatório por cidade (ativos x inativos)**  
  Quantidade e percentual de clientes ativos/inativos por cidade (filtrável por UF).
- **Relatório por UF (estado)**  
  Total, ativos, inativos e percentual de ativos por unidade da federação.
- **Relatório de clientes inativos**  
  Lista resumida de clientes com status inativo (também com opção de exportar CSV).
- **Dashboard de estatísticas gerais** (no menu principal)  
  - Total de clientes
  - Quantidade de ativos e inativos
  - Percentual de cada grupo

### Geração de Dados de Teste

- Script de geração de **dados fictícios realistas**, com:
  - Nomes e sobrenomes brasileiros
  - **CPFs válidos**
  - Endereços completos (rua, bairro, cidade, UF, CEP)
- Capaz de gerar **dezenas ou centenas de milhares de registros** rapidamente.
- Script específico para garantir que **todos os estados brasileiros** tenham clientes em várias cidades.

---

## 📁 Estrutura do Projeto

```text
gestao-clientes-mongodb/
├── dados/
│   ├── clientes_export.csv           # Export geral de clientes
│   ├── clientes_inativos.csv         # Export de clientes inativos
│   ├── clientes_por_cidade.csv       # Relatório de clientes por cidade
│   ├── clientes_por_faixa_etaria.csv # Relatório de clientes por faixa etária
│   └── clientes_por_uf.csv           # Relatório de clientes por UF
├── mongo-data/                       # Dados do MongoDB (volume Docker)
├── src/
│   ├── menu_principal.py             # Entrada principal do sistema (CLI)
│   ├── cliente_model.py              # Modelo de dados do cliente
│   ├── cliente_crud.py               # Operações CRUD sobre a coleção
│   ├── conexao.py                    # Conexão com o MongoDB
│   ├── backup_banco.py               # Backup da base de dados
│   ├── gerar_dados.py                # Geração básica de clientes fictícios
│   ├── gerar_clientes_cidades_reais.py  # Geração avançada (todas as UFs/cidades)
│   ├── post_setup_indices.py         # Criação de índices no MongoDB
│   ├── relatorio_export_csv.py       # Exportação geral de clientes para CSV
│   ├── relatorio_cidades.py          # Relatório de clientes por cidade
│   ├── relatorio_cidade_status.py    # Cidade x (ativos/inativos)
│   ├── relatorio_faixa_etaria.py     # Relatório por faixa etária
│   ├── relatorio_inativos.py         # Relatório de inativos (console)
│   ├── relatorio_inativos_csv.py     # Relatório de inativos (CSV)
│   ├── relatorio_uf.py               # Relatório por UF
│   └── teste_conexao.py              # Teste rápido de conexão com o banco
├── .env                              # Configurações da conexão MongoDB
├── docker-compose.yml                # Subir MongoDB via Docker
├── requirements.txt                  # Dependências Python
└── README.md
