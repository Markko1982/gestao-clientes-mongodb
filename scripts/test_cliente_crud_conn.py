"""
Teste de conexão e importação do ClienteCRUD usando config.py.

Mostra:
- sys.path relevante
- Erros de import com traceback
- DB e coleção conectados, se der tudo certo
"""

from pathlib import Path
import sys
import traceback

# Descobre a raiz do projeto (onde está config.py)
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for p in (ROOT, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

print(">>> ROOT:", ROOT)
print(">>> SRC :", SRC)
print(">>> Primeiros itens de sys.path:")
for p in sys.path[:5]:
    print("   -", p)

print("\n>>> Tentando importar ClienteCRUD...\n")

try:
    from cliente_crud import ClienteCRUD
except Exception:
    print("❌ Erro ao importar 'cliente_crud.ClienteCRUD':")
    traceback.print_exc()
    sys.exit(1)

print("✅ Import de ClienteCRUD OK. Agora testando conexão...\n")

try:
    crud = ClienteCRUD()
    print("\nDB conectado :", crud.db.name)
    print("Coleção      :", crud.colecao.name)
    crud.fechar_conexao()
    print("\n✅ Teste concluído com sucesso.")
except Exception:
    print("❌ Erro ao instanciar ClienteCRUD ou acessar db/colecao:")
    traceback.print_exc()
    sys.exit(1)
