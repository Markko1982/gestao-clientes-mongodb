from src.cliente_crud import ClienteCRUD
from src.cliente_model import Cliente
import os
from datetime import datetime
from src.relatorio_faixa_etaria import gerar_relatorio_faixa_etaria
from src.relatorio_cidades import gerar_relatorio_cidades
from src.dashboard_executivo import gerar_dashboard_executivo



def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('clear' if os.name != 'nt' else 'cls')

def pausar():
    """Pausa a execução até o usuário pressionar Enter"""
    input("\nPressione ENTER para continuar...")

def exibir_cabecalho():
    """Exibe o cabeçalho do sistema"""
    print("\n" + "="*70)
    print(" "*15 + "SISTEMA DE GESTÃO DE CLIENTES")
    print(" "*20 + "Empresa XYZ Ltda.")
    print("="*70 + "\n")

def exibir_cliente_detalhado(cliente: Cliente):
    """
    Exibe todos os dados de um cliente de forma formatada
    
    Args:
        cliente: Objeto Cliente a ser exibido
    """
    print("\n" + "-"*70)
    print(f"ID: {cliente._id}")
    print(f"Nome: {cliente.nome}")
    print(f"CPF: {cliente.cpf}")
    print(f"Email: {cliente.email}")
    print(f"Telefone: {cliente.telefone}")
    print(f"Data de Nascimento: {cliente.data_nascimento}")
    print(f"Status: {cliente.status.upper()}")
    print(f"\nEndereço:")
    print(f"  Rua: {cliente.endereco['rua']}, {cliente.endereco['numero']}")
    if cliente.endereco.get('complemento'):
        print(f"  Complemento: {cliente.endereco['complemento']}")
    print(f"  Bairro: {cliente.endereco['bairro']}")
    print(f"  Cidade: {cliente.endereco['cidade']} - {cliente.endereco['estado']}")
    print(f"  CEP: {cliente.endereco['cep']}")
    print(f"\nData de Cadastro: {cliente.data_cadastro}")
    print("-"*70)


def menu_buscar_cliente(crud: ClienteCRUD):
    """Menu de busca de clientes"""
    import unicodedata

    def normalizar(txt: str) -> str:
        """Remove acentos e converte para minúsculo para comparar."""
        if not txt:
            return ""
        txt = txt.strip().lower()
        return "".join(
            c for c in unicodedata.normalize("NFD", txt)
            if unicodedata.category(c) != "Mn"
        )

    limpar_tela()
    exibir_cabecalho()
    print("BUSCAR CLIENTE\n")

    print("1. Buscar por CPF (exato)")
    print("2. Buscar por nome (contém)")
    print("3. Buscar por cidade e estado")
    print("0. Voltar")

    opcao = input("\nEscolha uma opção: ").strip()

    if opcao == "0":
        return

    # --- Opção 1: CPF exato ---
    if opcao == "1":
        cpf = input("\nDigite o CPF do cliente: ").strip()
        cliente = crud.buscar_por_cpf(cpf)
        if cliente:
            exibir_cliente_detalhado(cliente)
        else:
            print("\n✗ Cliente não encontrado!")
        pausar()
        return

    # Carrega todos os clientes de uma vez
    todos = crud.listar_todos(0)  # 0 = sem limite

    if not todos:
        print("\n✗ Nenhum cliente cadastrado.")
        pausar()
        return

    # Limite de resultados
    try:
        limite_str = input("Quantos clientes deseja ver? (0 = todos): ").strip() or "20"
        limite = int(limite_str)
    except ValueError:
        print("\nValor inválido, usando limite padrão (20).")
        limite = 20

    filtrados = []

    # --- Opção 2: nome contém ---
    if opcao == "2":
        termo = input("\nTermo de busca no nome: ").strip()
        if not termo:
            print("\n✗ Termo de busca vazio.")
            pausar()
            return

        termo_norm = normalizar(termo)
        for c in todos:
            if termo_norm in normalizar(c.nome):
                filtrados.append(c)

    # --- Opção 3: cidade/UF ---
    elif opcao == "3":
        print("\nBuscar por cidade e estado (deixe em branco para não filtrar por um campo):")
        cidade_in = input("Cidade: ").strip()
        uf_in = input("UF (ex: SP): ").strip()

        cidade_norm = normalizar(cidade_in)
        uf_norm = normalizar(uf_in)

        for c in todos:
            end = c.endereco or {}
            cidade_cli = normalizar(end.get("cidade", ""))
            uf_cli = normalizar(end.get("estado", "") or end.get("uf", ""))

            if cidade_norm and cidade_norm not in cidade_cli:
                continue
            if uf_norm and uf_norm != uf_cli:
                continue
            filtrados.append(c)

    else:
        print("\n✗ Opção inválida.")
        pausar()
        return

    # Aplica limite e exibe
    if limite > 0:
        filtrados = filtrados[:limite]

    if filtrados:
        print(f"\n✓ {len(filtrados)} cliente(s) encontrado(s):\n")
        for i, cliente in enumerate(filtrados, 1):
            end = cliente.endereco or {}
            cidade_cli = end.get("cidade", "")
            uf_cli = end.get("estado", "") or end.get("uf", "")
            print(f"{i}. {cliente.nome} | CPF: {cliente.cpf} | Cidade: {cidade_cli} - {uf_cli} | Status: {cliente.status}")
    else:
        print("\n✗ Nenhum cliente encontrado com esses filtros.")

    pausar()
def menu_cadastrar_cliente(crud: ClienteCRUD):
    """Menu de cadastro de novo cliente"""
    limpar_tela()
    exibir_cabecalho()
    print("CADASTRAR NOVO CLIENTE\n")
    
    try:
        nome = input("Nome completo: ")
        cpf = input("CPF (apenas números): ")
        email = input("Email: ")
        telefone = input("Telefone (ex: (11) 98765-4321): ")
        data_nascimento = input("Data de nascimento (YYYY-MM-DD): ")
        
        print("\nEndereço:")
        rua = input("  Rua: ")
        numero = input("  Número: ")
        complemento = input("  Complemento (opcional): ")
        bairro = input("  Bairro: ")
        cidade = input("  Cidade: ")
        estado = input("  Estado (sigla): ")
        cep = input("  CEP: ")
        
        endereco = {
            "rua": rua,
            "numero": numero,
            "complemento": complemento,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        }
        
        cliente = Cliente(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            data_nascimento=data_nascimento,
            endereco=endereco
        )
        
        if crud.criar_cliente(cliente):
            print("\n✓ Cliente cadastrado com sucesso!")
        else:
            print("\n✗ Erro ao cadastrar cliente!")
            
    except Exception as e:
        print(f"\n✗ Erro: {e}")
    
    pausar()

def menu_atualizar_cliente(crud: ClienteCRUD):
    """Menu de atualização de cliente"""
    limpar_tela()
    exibir_cabecalho()
    print("ATUALIZAR CLIENTE\n")
    
    cpf = input("Digite o CPF do cliente: ")
    cliente = crud.buscar_por_cpf(cpf)
    
    if not cliente:
        print("\n✗ Cliente não encontrado!")
        pausar()
        return
    
    exibir_cliente_detalhado(cliente)
    
    print("\nO que deseja atualizar?")
    print("1. Email")
    print("2. Telefone")
    print("3. Endereço")
    print("4. Status")
    print("0. Cancelar")
    
    opcao = input("\nEscolha uma opção: ")
    
    novos_dados = {}
    
    if opcao == "1":
        novo_email = input("Novo email: ")
        novos_dados["email"] = novo_email
    elif opcao == "2":
        novo_telefone = input("Novo telefone: ")
        novos_dados["telefone"] = novo_telefone
    elif opcao == "3":
        print("\nNovo endereço:")
        rua = input("  Rua: ")
        numero = input("  Número: ")
        complemento = input("  Complemento: ")
        bairro = input("  Bairro: ")
        cidade = input("  Cidade: ")
        estado = input("  Estado: ")
        cep = input("  CEP: ")
        novos_dados["endereco"] = {
            "rua": rua, "numero": numero, "complemento": complemento,
            "bairro": bairro, "cidade": cidade, "estado": estado, "cep": cep
        }
    elif opcao == "4":
        print("\nStatus:")
        print("1. Ativo")
        print("2. Inativo")
        status_opcao = input("Escolha: ")
        novos_dados["status"] = "ativo" if status_opcao == "1" else "inativo"
    
    if novos_dados:
        crud.atualizar_cliente(cpf, novos_dados)
    
    pausar()

def menu_listar_clientes(crud: ClienteCRUD):
    """Menu de listagem de clientes"""
    limpar_tela()
    exibir_cabecalho()
    print("LISTAR CLIENTES\n")
    
    print("1. Listar todos os clientes")
    print("2. Listar apenas ativos")
    print("3. Listar apenas inativos")
    print("0. Voltar")
    
    opcao = input("\nEscolha uma opção: ")

    try:
        limite_str = input("Quantos clientes deseja ver? (0 = todos, ENTER = 20): ").strip()
        limite = int(limite_str) if limite_str else 20
    except ValueError:
        print("\nValor inválido, usando limite padrão (20).")
        limite = 20

    # Busca todos os clientes e só depois aplica filtro/limite
    todos = crud.listar_todos(0)

    if opcao == "1":
        clientes = todos
    elif opcao == "2":
        clientes = [c for c in todos if c.status == "ativo"]
    elif opcao == "3":
        clientes = [c for c in todos if c.status == "inativo"]
    else:
        return

    if limite > 0:
        clientes = clientes[:limite]
    
    if clientes:
        print(f"\n✓ {len(clientes)} cliente(s) encontrado(s):\n")
        for i, cliente in enumerate(clientes, 1):
            print(f"{i}. {cliente.nome} | CPF: {cliente.cpf} | Status: {cliente.status}")
    else:
        print("\n✗ Nenhum cliente encontrado!")
    
    pausar()

def menu_estatisticas(crud: ClienteCRUD):
    """Menu de estatísticas do sistema"""
    limpar_tela()
    exibir_cabecalho()
    print("ESTATÍSTICAS DO SISTEMA\n")
    
    total = crud.contar_clientes()
    ativos = crud.contar_clientes({"status": "ativo"})
    inativos = crud.contar_clientes({"status": "inativo"})
    
    print(f"📊 Total de clientes: {total}")
    print(f"✓ Clientes ativos: {ativos} ({ativos/total*100:.1f}%)")
    print(f"✗ Clientes inativos: {inativos} ({inativos/total*100:.1f}%)")
    
    pausar()

def menu_principal():
    """Menu principal do sistema"""
    crud = ClienteCRUD()
    
    while True:
        limpar_tela()
        exibir_cabecalho()
        
        print("1. Buscar Cliente")
        print("2. Cadastrar Novo Cliente")
        print("3. Atualizar Cliente")
        print("4. Listar Clientes")
        print("5. Inativar Cliente")
        print("6. Deletar Cliente")
        print("7. Estatísticas")
        print("8. Relatório por faixa etária")
        print("9. Relatório por cidades")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            menu_buscar_cliente(crud)
        elif opcao == "2":
            menu_cadastrar_cliente(crud)
        elif opcao == "3":
            menu_atualizar_cliente(crud)
        elif opcao == "4":
            menu_listar_clientes(crud)
        elif opcao == "5":
            cpf = input("\nDigite o CPF do cliente a inativar: ")
            crud.inativar_cliente(cpf)
            pausar()
        elif opcao == "6":
            cpf = input("\nDigite o CPF do cliente a deletar: ")
            confirmacao = input("Tem certeza? (S/N): ")
            if confirmacao.upper() == "S":
                crud.deletar_cliente(cpf)
            pausar()
        elif opcao == "7":
            menu_estatisticas(crud)
        elif opcao == "8":
            gerar_relatorio_faixa_etaria()
            pausar()
        elif opcao == "9":
            gerar_relatorio_cidades()
            pausar()
        elif opcao == "0":
            print("\n✓ Encerrando sistema...")
            crud.fechar_conexao()
            break
        else:
            print("\n✗ Opção inválida!")
            pausar()

if __name__ == "__main__":
    menu_principal()
