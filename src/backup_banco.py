from cliente_crud import ClienteCRUD
from datetime import datetime
import json
import os

def fazer_backup():
    """
    Faz backup completo do banco de dados MongoDB
    Exporta todos os clientes para arquivo JSON
    """
    print("\n" + "="*80)
    print(" "*25 + "BACKUP DO BANCO DE DADOS")
    print(" "*30 + "Sistema de TI")
    print("="*80 + "\n")
    
    # Conectar ao banco
    crud = ClienteCRUD()
    
    print("📊 Iniciando backup...")
    inicio = datetime.now()
    
    # Buscar todos os clientes
    print("📥 Coletando dados do MongoDB...")
    todos_clientes = crud.listar_todos()
    total = len(todos_clientes)
    
    print(f"✓ {total:,} clientes encontrados\n")
    
    # Converter para dicionários (formato JSON)
    print("🔄 Convertendo para formato JSON...")
    dados_backup = []
    
    for i, cliente in enumerate(todos_clientes, 1):
        dados_backup.append(cliente.to_dict())
        
        # Mostrar progresso a cada 10000
        if i % 10000 == 0:
            print(f"   Processados: {i:,}/{total:,} ({(i/total)*100:.1f}%)")
    
    print(f"✓ Todos os {total:,} clientes convertidos\n")
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"backup_clientes_{timestamp}.json"
    
    # Salvar em JSON
    print(f"💾 Salvando backup em: {nome_arquivo}")
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados_backup, f, ensure_ascii=False, indent=2, default=str)
    
    # Verificar tamanho do arquivo
    tamanho_bytes = os.path.getsize(nome_arquivo)
    tamanho_mb = tamanho_bytes / (1024 * 1024)
    
    fim = datetime.now()
    tempo_decorrido = (fim - inicio).total_seconds()
    
    # Relatório do backup
    print("\n" + "="*80)
    print("RELATÓRIO DO BACKUP")
    print("="*80)
    
    print(f"\n✅ Backup concluído com sucesso!")
    print(f"\n📊 Estatísticas:")
    print(f"   • Total de registros: {total:,}")
    print(f"   • Arquivo gerado: {nome_arquivo}")
    print(f"   • Tamanho: {tamanho_mb:.2f} MB ({tamanho_bytes:,} bytes)")
    print(f"   • Tempo de execução: {tempo_decorrido:.2f} segundos")
    print(f"   • Velocidade: {total/tempo_decorrido:.0f} registros/segundo")
    
    # Informações adicionais
    print(f"\n📁 Localização: {os.path.abspath(nome_arquivo)}")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Instruções de restauração
    print("\n" + "="*80)
    print("INSTRUÇÕES PARA RESTAURAÇÃO")
    print("="*80)
    print(f"\nPara restaurar este backup:")
    print(f"1. Abra o arquivo: {nome_arquivo}")
    print(f"2. Use o script de importação (a ser criado)")
    print(f"3. Ou importe manualmente via MongoDB Compass")
    
    # Recomendações
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÕES DE SEGURANÇA")
    print("="*80)
    print("\n1. Copie este arquivo para um local seguro (nuvem, servidor backup)")
    print("2. Faça backups regulares (diário, semanal)")
    print("3. Mantenha múltiplas versões de backup")
    print("4. Teste a restauração periodicamente")
    print("5. Criptografe backups com dados sensíveis")
    
    print("\n" + "="*80 + "\n")
    
    crud.fechar_conexao()
    
    return nome_arquivo

def verificar_backup(nome_arquivo):
    """
    Verifica integridade de um arquivo de backup
    """
    print(f"\n🔍 Verificando backup: {nome_arquivo}\n")
    
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        print(f"✅ Arquivo válido!")
        print(f"📊 Registros encontrados: {len(dados):,}")
        
        # Verificar estrutura do primeiro registro
        if dados:
            primeiro = dados[0]
            campos = list(primeiro.keys())
            print(f"📋 Campos por registro: {len(campos)}")
            print(f"🔑 Campos: {', '.join(campos[:5])}...")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Erro: Arquivo JSON inválido!")
        return False
    except FileNotFoundError:
        print("❌ Erro: Arquivo não encontrado!")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    # Fazer backup
    arquivo_backup = fazer_backup()
    
    # Verificar integridade
    print("\n" + "="*80)
    print("VERIFICAÇÃO DE INTEGRIDADE")
    print("="*80)
    verificar_backup(arquivo_backup)
