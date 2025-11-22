from cliente_crud import ClienteCRUD
from datetime import datetime
import csv

def calcular_idade(data_nascimento_str: str) -> int:
    """
    Calcula a idade a partir da data de nascimento
    
    Args:
        data_nascimento_str: Data no formato YYYY-MM-DD
        
    Returns:
        Idade em anos
    """
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - data_nascimento.year
        
        # Ajusta se ainda não fez aniversário este ano
        if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
            idade -= 1
            
        return idade
    except:
        return 0

def classificar_faixa_etaria(idade: int) -> str:
    """
    Classifica a idade em faixa etária
    
    Args:
        idade: Idade em anos
        
    Returns:
        Nome da faixa etária
    """
    if idade < 18:
        return "Menor de 18"
    elif 18 <= idade <= 25:
        return "18-25 anos"
    elif 26 <= idade <= 35:
        return "26-35 anos"
    elif 36 <= idade <= 50:
        return "36-50 anos"
    elif 51 <= idade <= 65:
        return "51-65 anos"
    else:
        return "65+ anos"

def buscar_por_faixa_etaria(faixa: str):
    """
    Busca clientes por faixa etária específica
    
    Args:
        faixa: Nome da faixa etária
        
    Returns:
        Lista de clientes da faixa
    """
    crud = ClienteCRUD()
    todos_clientes = crud.listar_todos()
    
    clientes_faixa = []
    
    for cliente in todos_clientes:
        idade = calcular_idade(cliente.data_nascimento)
        faixa_cliente = classificar_faixa_etaria(idade)
        
        if faixa_cliente == faixa:
            clientes_faixa.append({
                'cliente': cliente,
                'idade': idade
            })
    
    crud.fechar_conexao()
    return clientes_faixa

def gerar_relatorio_faixas_etarias():
    """
    Gera relatório completo de distribuição por faixa etária
    """
    print("\n" + "="*80)
    print(" "*20 + "RELATÓRIO DE FAIXAS ETÁRIAS")
    print("="*80 + "\n")
    
    crud = ClienteCRUD()
    
    print("📊 Analisando clientes...")
    todos_clientes = crud.listar_todos()
    total = len(todos_clientes)
    
    # Dicionário para contar por faixa
    faixas = {
        "Menor de 18": 0,
        "18-25 anos": 0,
        "26-35 anos": 0,
        "36-50 anos": 0,
        "51-65 anos": 0,
        "65+ anos": 0
    }
    
    # Classificar todos os clientes
    for cliente in todos_clientes:
        idade = calcular_idade(cliente.data_nascimento)
        faixa = classificar_faixa_etaria(idade)
        faixas[faixa] += 1
    
    # Exibir resultados
    print("\n" + "="*80)
    print(f"{'FAIXA ETÁRIA':<20} {'QUANTIDADE':<15} {'PERCENTUAL':<15} {'BARRA':<30}")
    print("="*80)
    
    for faixa, quantidade in faixas.items():
        percentual = (quantidade / total) * 100
        barra = "█" * int(percentual / 2)  # Cada █ = 2%
        print(f"{faixa:<20} {quantidade:<15} {percentual:>6.2f}%        {barra}")
    
    print("="*80)
    print(f"\nTotal de clientes analisados: {total:,}")
    
    # Estatísticas adicionais
    print("\n" + "="*80)
    print("INSIGHTS PARA MARKETING:")
    print("="*80)
    
    # Maior faixa
    maior_faixa = max(faixas.items(), key=lambda x: x[1])
    print(f"\n🎯 Maior público: {maior_faixa[0]} ({maior_faixa[1]:,} clientes)")
    
    # Faixas prioritárias (acima de 15%)
    print(f"\n📈 Faixas prioritárias (>15% do total):")
    for faixa, qtd in faixas.items():
        perc = (qtd / total) * 100
        if perc > 15:
            print(f"   • {faixa}: {qtd:,} clientes ({perc:.1f}%)")
    
    # Exportar para CSV
    nome_arquivo = f"relatorio_faixas_etarias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['faixa_etaria', 'quantidade', 'percentual']
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        
        writer.writeheader()
        
        for faixa, quantidade in faixas.items():
            percentual = (quantidade / total) * 100
            writer.writerow({
                'faixa_etaria': faixa,
                'quantidade': quantidade,
                'percentual': f"{percentual:.2f}%"
            })
    
    print(f"\n✓ Relatório exportado para: {nome_arquivo}")
    print("="*80 + "\n")
    
    crud.fechar_conexao()

def exportar_faixa_especifica(faixa: str):
    """
    Exporta clientes de uma faixa etária específica para CSV
    
    Args:
        faixa: Nome da faixa etária
    """
    print(f"\n📊 Buscando clientes da faixa: {faixa}...")
    
    clientes_faixa = buscar_por_faixa_etaria(faixa)
    
    if not clientes_faixa:
        print(f"✗ Nenhum cliente encontrado na faixa {faixa}")
        return
    
    # Nome do arquivo
    faixa_limpa = faixa.replace(" ", "_").replace("+", "mais")
    nome_arquivo = f"clientes_{faixa_limpa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Exportar
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['nome', 'cpf', 'email', 'telefone', 'idade', 'cidade', 'estado', 'status']
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        
        writer.writeheader()
        
        for item in clientes_faixa:
            cliente = item['cliente']
            idade = item['idade']
            
            writer.writerow({
                'nome': cliente.nome,
                'cpf': cliente.cpf,
                'email': cliente.email,
                'telefone': cliente.telefone,
                'idade': idade,
                'cidade': cliente.endereco.get('cidade', ''),
                'estado': cliente.endereco.get('estado', ''),
                'status': cliente.status
            })
    
    print(f"✓ {len(clientes_faixa)} clientes exportados para: {nome_arquivo}\n")

# Menu interativo
def menu_faixas_etarias():
    """Menu interativo para análise por faixa etária"""
    while True:
        print("\n" + "="*80)
        print(" "*25 + "ANÁLISE POR FAIXA ETÁRIA")
        print("="*80)
        print("\n1. Ver relatório geral de todas as faixas")
        print("2. Exportar clientes de faixa específica")
        print("3. Buscar clientes por idade exata")
        print("0. Voltar")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            gerar_relatorio_faixas_etarias()
            input("\nPressione ENTER para continuar...")
            
        elif opcao == "2":
            print("\nFaixas disponíveis:")
            print("1. 18-25 anos")
            print("2. 26-35 anos")
            print("3. 36-50 anos")
            print("4. 51-65 anos")
            print("5. 65+ anos")
            
            escolha = input("\nEscolha a faixa: ")
            
            faixas_map = {
                "1": "18-25 anos",
                "2": "26-35 anos",
                "3": "36-50 anos",
                "4": "51-65 anos",
                "5": "65+ anos"
            }
            
            if escolha in faixas_map:
                exportar_faixa_especifica(faixas_map[escolha])
            input("\nPressione ENTER para continuar...")
            
        elif opcao == "3":
            idade = input("\nDigite a idade: ")
            if idade.isdigit():
                faixa = classificar_faixa_etaria(int(idade))
                print(f"\nIdade {idade} anos pertence à faixa: {faixa}")
            input("\nPressione ENTER para continuar...")
            
        elif opcao == "0":
            break

if __name__ == "__main__":
    menu_faixas_etarias()
