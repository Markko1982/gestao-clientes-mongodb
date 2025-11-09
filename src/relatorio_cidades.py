from cliente_crud import ClienteCRUD
import csv
from datetime import datetime
from collections import Counter

def gerar_relatorio_por_cidade():
    """
    Gera relatório de clientes agrupados por cidade
    Exporta para CSV e exibe no terminal
    """
    print("\n" + "="*80)
    print(" "*20 + "RELATÓRIO DE CLIENTES POR CIDADE")
    print("="*80 + "\n")
    
    # Conectar ao banco
    crud = ClienteCRUD()
    
    print("📊 Coletando dados do banco...")
    
    # Buscar todos os clientes
    clientes = crud.listar_todos()
    total_clientes = len(clientes)
    
    print(f"✓ Total de clientes analisados: {total_clientes}\n")
    
    # Agrupar por cidade e estado
    cidades_dict = {}
    
    for cliente in clientes:
        cidade = cliente.endereco.get('cidade', 'Não informado')
        estado = cliente.endereco.get('estado', 'N/A')
        chave = f"{cidade} - {estado}"
        
        if chave in cidades_dict:
            cidades_dict[chave]['quantidade'] += 1
        else:
            cidades_dict[chave] = {
                'cidade': cidade,
                'estado': estado,
                'quantidade': 1
            }
    
    # Converter para lista e ordenar por quantidade (maior para menor)
    cidades_lista = []
    for chave, dados in cidades_dict.items():
        percentual = (dados['quantidade'] / total_clientes) * 100
        cidades_lista.append({
            'cidade': dados['cidade'],
            'estado': dados['estado'],
            'quantidade': dados['quantidade'],
            'percentual': percentual
        })
    
    # Ordenar por quantidade (decrescente)
    cidades_lista.sort(key=lambda x: x['quantidade'], reverse=True)
    
    # Exibir no terminal (top 20)
    print("="*80)
    print(f"{'#':<5} {'CIDADE':<30} {'ESTADO':<8} {'CLIENTES':<12} {'%':<10}")
    print("="*80)
    
    for i, cidade in enumerate(cidades_lista[:20], 1):
        print(f"{i:<5} {cidade['cidade']:<30} {cidade['estado']:<8} "
              f"{cidade['quantidade']:<12} {cidade['percentual']:.2f}%")
    
    print("="*80)
    print(f"\nTotal de cidades diferentes: {len(cidades_lista)}")
    
    # Exportar para CSV
    nome_arquivo = f"relatorio_cidades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['posicao', 'cidade', 'estado', 'quantidade_clientes', 'percentual']
        writer = csv.DictWriter(arquivo_csv, fieldnames=campos)
        
        writer.writeheader()
        
        for i, cidade in enumerate(cidades_lista, 1):
            writer.writerow({
                'posicao': i,
                'cidade': cidade['cidade'],
                'estado': cidade['estado'],
                'quantidade_clientes': cidade['quantidade'],
                'percentual': f"{cidade['percentual']:.2f}%"
            })
    
    print(f"\n✓ Relatório completo exportado para: {nome_arquivo}")
    print(f"✓ Total de {len(cidades_lista)} cidades no arquivo CSV\n")
    
    # Estatísticas extras
    print("="*80)
    print("ESTATÍSTICAS ADICIONAIS:")
    print("="*80)
    
    # Top 5 estados com mais clientes
    estados_counter = Counter([c['estado'] for c in cidades_lista])
    print("\n📍 Top 5 Estados com mais cidades representadas:")
    for estado, qtd in estados_counter.most_common(5):
        print(f"   {estado}: {qtd} cidades")
    
    # Cidade com mais clientes
    top_cidade = cidades_lista[0]
    print(f"\n🏆 Cidade com mais clientes:")
    print(f"   {top_cidade['cidade']} - {top_cidade['estado']}: "
          f"{top_cidade['quantidade']} clientes ({top_cidade['percentual']:.2f}%)")
    
    print("\n" + "="*80 + "\n")
    
    crud.fechar_conexao()

if __name__ == "__main__":
    gerar_relatorio_por_cidade()
