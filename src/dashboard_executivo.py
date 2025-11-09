from cliente_crud import ClienteCRUD
from datetime import datetime, timedelta
from collections import Counter
import csv

def calcular_idade(data_nascimento_str: str) -> int:
    """Calcula idade a partir da data de nascimento"""
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - data_nascimento.year
        if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
            idade -= 1
        return idade
    except:
        return 0

def gerar_dashboard_executivo():
    """
    Gera dashboard executivo com estatísticas avançadas para a diretoria
    """
    print("\n" + "="*90)
    print(" "*25 + "DASHBOARD EXECUTIVO")
    print(" "*30 + "DIRETORIA")
    print(" "*20 + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("="*90 + "\n")
    
    # Conectar ao banco
    crud = ClienteCRUD()
    
    print("📊 Coletando dados do sistema...\n")
    
    # Buscar todos os clientes
    todos_clientes = crud.listar_todos()
    total_clientes = len(todos_clientes)
    
    # ========== 1. VISÃO GERAL ==========
    print("="*90)
    print("1. VISÃO GERAL DO SISTEMA")
    print("="*90)
    
    clientes_ativos = len([c for c in todos_clientes if c.status == "ativo"])
    clientes_inativos = len([c for c in todos_clientes if c.status == "inativo"])
    taxa_ativacao = (clientes_ativos / total_clientes) * 100
    
    print(f"\n📊 Total de Clientes: {total_clientes:,}")
    print(f"✅ Clientes Ativos: {clientes_ativos:,} ({taxa_ativacao:.1f}%)")
    print(f"❌ Clientes Inativos: {clientes_inativos:,} ({100-taxa_ativacao:.1f}%)")
    
    # ========== 2. MÉDIA DE IDADE ==========
    print("\n" + "="*90)
    print("2. ANÁLISE DEMOGRÁFICA")
    print("="*90)
    
    idades = [calcular_idade(c.data_nascimento) for c in todos_clientes]
    idades_validas = [i for i in idades if i > 0]
    
    if idades_validas:
        media_idade = sum(idades_validas) / len(idades_validas)
        idade_min = min(idades_validas)
        idade_max = max(idades_validas)
        
        print(f"\n👥 Média de Idade: {media_idade:.1f} anos")
        print(f"📉 Idade Mínima: {idade_min} anos")
        print(f"📈 Idade Máxima: {idade_max} anos")
    
    # ========== 3. CLIENTES NOVOS (ÚLTIMOS 30 DIAS) ==========
    print("\n" + "="*90)
    print("3. NOVOS CADASTROS")
    print("="*90)
    
    hoje = datetime.now()
    data_30_dias = hoje - timedelta(days=30)
    
    novos_30_dias = 0
    for cliente in todos_clientes:
        data_cadastro = cliente.data_cadastro
        if isinstance(data_cadastro, str):
            data_cadastro = datetime.fromisoformat(data_cadastro)
        
        if data_cadastro >= data_30_dias:
            novos_30_dias += 1
    
    print(f"\n📅 Últimos 30 dias: {novos_30_dias:,} novos clientes")
    print(f"📊 Média diária: {novos_30_dias/30:.1f} clientes/dia")
    
    # ========== 4. CADASTROS POR MÊS (ÚLTIMOS 12 MESES) ==========
    print("\n" + "="*90)
    print("4. EVOLUÇÃO MENSAL (ÚLTIMOS 12 MESES)")
    print("="*90 + "\n")
    
    # Preparar dicionário de meses
    cadastros_por_mes = {}
    for i in range(12):
        mes_ref = hoje - timedelta(days=30*i)
        chave_mes = mes_ref.strftime("%Y-%m")
        cadastros_por_mes[chave_mes] = 0
    
    # Contar cadastros por mês
    for cliente in todos_clientes:
        data_cadastro = cliente.data_cadastro
        if isinstance(data_cadastro, str):
            data_cadastro = datetime.fromisoformat(data_cadastro)
        
        chave_mes = data_cadastro.strftime("%Y-%m")
        if chave_mes in cadastros_por_mes:
            cadastros_por_mes[chave_mes] += 1
    
    # Ordenar por data
    meses_ordenados = sorted(cadastros_por_mes.items(), reverse=True)
    
    print(f"{'MÊS':<15} {'CADASTROS':<15} {'GRÁFICO':<40}")
    print("-"*90)
    
    max_cadastros = max(cadastros_por_mes.values()) if cadastros_por_mes.values() else 1
    
    for mes, qtd in meses_ordenados:
        # Converter para nome do mês
        data_mes = datetime.strptime(mes, "%Y-%m")
        nome_mes = data_mes.strftime("%b/%Y")
        
        # Gráfico de barras
        barra_tamanho = int((qtd / max_cadastros) * 30) if max_cadastros > 0 else 0
        barra = "█" * barra_tamanho
        
        print(f"{nome_mes:<15} {qtd:<15,} {barra}")
    
    # Taxa de crescimento
    if len(meses_ordenados) >= 2:
        mes_atual = meses_ordenados[0][1]
        mes_anterior = meses_ordenados[1][1]
        
        if mes_anterior > 0:
            taxa_crescimento = ((mes_atual - mes_anterior) / mes_anterior) * 100
            simbolo = "📈" if taxa_crescimento > 0 else "📉"
            print(f"\n{simbolo} Taxa de crescimento (mês atual vs anterior): {taxa_crescimento:+.1f}%")
    
    # ========== 5. DISTRIBUIÇÃO POR ESTADO ==========
    print("\n" + "="*90)
    print("5. DISTRIBUIÇÃO GEOGRÁFICA (TOP 10 ESTADOS)")
    print("="*90 + "\n")
    
    estados = [c.endereco.get('estado', 'N/A') for c in todos_clientes]
    contador_estados = Counter(estados)
    top_10_estados = contador_estados.most_common(10)
    
    print(f"{'#':<5} {'ESTADO':<10} {'CLIENTES':<15} {'%':<10} {'GRÁFICO':<30}")
    print("-"*90)
    
    for i, (estado, qtd) in enumerate(top_10_estados, 1):
        percentual = (qtd / total_clientes) * 100
        barra = "█" * int(percentual)
        print(f"{i:<5} {estado:<10} {qtd:<15,} {percentual:>6.2f}%   {barra}")
    
    # ========== 6. DISTRIBUIÇÃO POR CIDADE (TOP 5) ==========
    print("\n" + "="*90)
    print("6. TOP 5 CIDADES COM MAIS CLIENTES")
    print("="*90 + "\n")
    
    cidades = [f"{c.endereco.get('cidade', 'N/A')} - {c.endereco.get('estado', 'N/A')}" 
               for c in todos_clientes]
    contador_cidades = Counter(cidades)
    top_5_cidades = contador_cidades.most_common(5)
    
    print(f"{'#':<5} {'CIDADE - ESTADO':<40} {'CLIENTES':<15} {'%':<10}")
    print("-"*90)
    
    for i, (cidade, qtd) in enumerate(top_5_cidades, 1):
        percentual = (qtd / total_clientes) * 100
        print(f"{i:<5} {cidade:<40} {qtd:<15,} {percentual:>6.2f}%")
    
    # ========== 7. RESUMO EXECUTIVO ==========
    print("\n" + "="*90)
    print("7. RESUMO EXECUTIVO - PRINCIPAIS INSIGHTS")
    print("="*90)
    
    print(f"\n✅ Base total de {total_clientes:,} clientes com taxa de ativação de {taxa_ativacao:.1f}%")
    print(f"👥 Perfil médio: {media_idade:.0f} anos")
    print(f"📈 Crescimento: {novos_30_dias:,} novos clientes nos últimos 30 dias")
    print(f"🗺️  Presença nacional: {len(contador_estados)} estados")
    print(f"🏆 Estado líder: {top_10_estados[0][0]} com {top_10_estados[0][1]:,} clientes")
    print(f"🏙️  Cidade líder: {top_5_cidades[0][0]} com {top_5_cidades[0][1]:,} clientes")
    
    # ========== EXPORTAR PARA CSV ==========
    print("\n" + "="*90)
    print("EXPORTANDO DADOS...")
    print("="*90)
    
    # CSV 1: Resumo Geral
    nome_arquivo_resumo = f"dashboard_resumo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(nome_arquivo_resumo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['MÉTRICA', 'VALOR'])
        writer.writerow(['Total de Clientes', total_clientes])
        writer.writerow(['Clientes Ativos', clientes_ativos])
        writer.writerow(['Clientes Inativos', clientes_inativos])
        writer.writerow(['Taxa de Ativação (%)', f"{taxa_ativacao:.2f}"])
        writer.writerow(['Média de Idade', f"{media_idade:.1f}"])
        writer.writerow(['Novos Clientes (30 dias)', novos_30_dias])
        writer.writerow(['Estados Cobertos', len(contador_estados)])
    
    print(f"✓ Resumo exportado: {nome_arquivo_resumo}")
    
    # CSV 2: Distribuição por Estado
    nome_arquivo_estados = f"dashboard_estados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(nome_arquivo_estados, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['POSICAO', 'ESTADO', 'QUANTIDADE', 'PERCENTUAL'])
        for i, (estado, qtd) in enumerate(top_10_estados, 1):
            perc = (qtd / total_clientes) * 100
            writer.writerow([i, estado, qtd, f"{perc:.2f}%"])
    
    print(f"✓ Ranking de estados exportado: {nome_arquivo_estados}")
    
    # CSV 3: Evolução Mensal
    nome_arquivo_mensal = f"dashboard_evolucao_mensal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(nome_arquivo_mensal, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['MES', 'CADASTROS'])
        for mes, qtd in meses_ordenados:
            writer.writerow([mes, qtd])
    
    print(f"✓ Evolução mensal exportada: {nome_arquivo_mensal}")
    
    print("\n" + "="*90)
    print("✅ DASHBOARD EXECUTIVO GERADO COM SUCESSO!")
    print("="*90 + "\n")
    
    crud.fechar_conexao()

if __name__ == "__main__":
    gerar_dashboard_executivo()
