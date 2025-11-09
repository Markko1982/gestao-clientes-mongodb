from cliente_crud import ClienteCRUD
from datetime import datetime
import csv

def gerar_relatorio_inativos():
    """
    Gera relatório de clientes inativos para campanha de reativação
    """
    print("\n" + "="*80)
    print(" "*20 + "RELATÓRIO DE CLIENTES INATIVOS")
    print(" "*22 + "Time de Retenção")
    print("="*80 + "\n")
    
    # Conectar ao banco
    crud = ClienteCRUD()
    
    print("📊 Buscando clientes inativos...")
    
    # Buscar todos os clientes
    todos_clientes = crud.listar_todos()
    
    # Filtrar apenas inativos
    clientes_inativos = [c for c in todos_clientes if c.status == "inativo"]
    
    print(f"✓ {len(clientes_inativos)} clientes inativos encontrados\n")
    
    if not clientes_inativos:
        print("✗ Nenhum cliente inativo encontrado!")
        crud.fechar_conexao()
        return
    
    # Preparar dados com dias de inatividade
    dados_relatorio = []
    hoje = datetime.now()
    
    for cliente in clientes_inativos:
        # Calcular dias desde o cadastro
        data_cadastro = cliente.data_cadastro
        if isinstance(data_cadastro, str):
            data_cadastro = datetime.fromisoformat(data_cadastro)
        
        dias_desde_cadastro = (hoje - data_cadastro).days
        
        dados_relatorio.append({
            'nome': cliente.nome,
            'cpf': cliente.cpf,
            'email': cliente.email,
            'telefone': cliente.telefone,
            'data_cadastro': data_cadastro.strftime("%Y-%m-%d"),
            'dias_inativo': dias_desde_cadastro,
            'cidade': cliente.endereco.get('cidade', ''),
            'estado': cliente.endereco.get('estado', '')
        })
    
    # Ordenar por data de cadastro (mais antigos primeiro)
    dados_relatorio.sort(key=lambda x: x['data_cadastro'])
    
    # Exibir preview (primeiros 10)
    print("="*80)
    print("PREVIEW - 10 PRIMEIROS CLIENTES INATIVOS (MAIS ANTIGOS):")
    print("="*80)
    print(f"{'NOME':<30} {'CPF':<15} {'CADASTRO':<12} {'DIAS INATIVO':<15}")
    print("="*80)
    
    for i, cliente in enumerate(dados_relatorio[:10], 1):
        print(f"{cliente['nome']:<30} {cliente['cpf']:<15} "
              f"{cliente['data_cadastro']:<12} {cliente['dias_inativo']:<15}")
    
    print("="*80)
    
    # Estatísticas
    print("\nESTATÍSTICAS:")
    print("="*80)
    
    total_inativos = len(dados_relatorio)
    media_dias = sum(c['dias_inativo'] for c in dados_relatorio) / total_inativos
    mais_antigo = max(dados_relatorio, key=lambda x: x['dias_inativo'])
    
    print(f"📊 Total de clientes inativos: {total_inativos:,}")
    print(f"📅 Média de dias inativos: {media_dias:.0f} dias")
    print(f"⏰ Cliente inativo há mais tempo: {mais_antigo['dias_inativo']} dias")
    
    # Segmentação por tempo de inatividade
    print(f"\n📈 SEGMENTAÇÃO POR TEMPO DE INATIVIDADE:")
    
    menos_30 = len([c for c in dados_relatorio if c['dias_inativo'] < 30])
    de_30_90 = len([c for c in dados_relatorio if 30 <= c['dias_inativo'] < 90])
    de_90_180 = len([c for c in dados_relatorio if 90 <= c['dias_inativo'] < 180])
    de_180_365 = len([c for c in dados_relatorio if 180 <= c['dias_inativo'] < 365])
    mais_365 = len([c for c in dados_relatorio if c['dias_inativo'] >= 365])
    
    print(f"   • Menos de 30 dias: {menos_30:,} clientes")
    print(f"   • 30-90 dias: {de_30_90:,} clientes")
    print(f"   • 90-180 dias: {de_90_180:,} clientes")
    print(f"   • 180-365 dias: {de_180_365:,} clientes")
    print(f"   • Mais de 1 ano: {mais_365:,} clientes")
    
    # Exportar para CSV
    nome_arquivo = f"clientes_inativos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['nome', 'cpf', 'email', 'telefone', 'cidade', 'estado', 
                  'data_cadastro', 'dias_inativo']
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        
        writer.writeheader()
        writer.writerows(dados_relatorio)
    
    print(f"\n✓ Relatório completo exportado para: {nome_arquivo}")
    print(f"✓ Total de {total_inativos:,} clientes inativos no arquivo CSV")
    
    # Recomendações
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÕES PARA CAMPANHA DE REATIVAÇÃO:")
    print("="*80)
    print("1. Priorizar clientes inativos há menos de 90 dias (maior chance de retorno)")
    print("2. Criar campanha especial para clientes há mais de 1 ano inativos")
    print("3. Segmentar comunicação por tempo de inatividade")
    print("4. Oferecer incentivos proporcionais ao tempo de inatividade")
    print("="*80 + "\n")
    
    crud.fechar_conexao()

if __name__ == "__main__":
    gerar_relatorio_inativos()
