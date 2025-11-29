import re
from src.cliente_crud import ClienteCRUD

def somente_digitos(s: str) -> str:
    return re.sub(r'\D+', '', s or '')

def main():
    termo = input("Digite parte do nome: ").strip()
    if not termo:
        print("✗ Termo vazio.")
        return

    crud = ClienteCRUD()
    resultados = crud.buscar_por_nome(termo)

    if not resultados:
        print("✗ Nenhum cliente encontrado.")
        crud.fechar_conexao()
        return

    print(f"\nEncontrados {len(resultados)} registro(s):")
    for i, c in enumerate(resultados, 1):
        print(f"{i:2d}) Nome: {c.nome} | CPF: {c.cpf} | Status: {c.status}")

    try:
        idx = int(input("\nEscolha o número do cliente para alternar status: ").strip())
    except Exception:
        print("✗ Entrada inválida.")
        crud.fechar_conexao()
        return

    if not (1 <= idx <= len(resultados)):
        print("✗ Número fora do intervalo.")
        crud.fechar_conexao()
        return

    c = resultados[idx - 1]
    cpf_norm = somente_digitos(c.cpf)

    print(f"\nSelecionado: {c.nome} | CPF normalizado: {cpf_norm} | Status atual: {c.status}")
    novo_status = "inativo" if c.status != "inativo" else "ativo"
    ok = crud.atualizar_cliente(cpf_norm, {"status": novo_status})

    if ok:
        c2 = crud.buscar_por_cpf(cpf_norm)
        print(f"✓ Status atualizado para: {c2.status}")
    else:
        print("✗ Falha ao atualizar status.")

    crud.fechar_conexao()

if __name__ == "__main__":
    main()
