"""
Analisa documentos da coleção 'clientes' e identifica registros que
não passariam no jsonSchema atual.

⚠ IMPORTANTE:
- Este script NÃO altera nada no banco.
- Agora ignora documentos marcados_para_exclusao = true (soft delete).
"""

import re
from pprint import pprint
from config import get_collection

REQUIRED_FIELDS = ["nome", "cpf", "email", "telefone", "status", "endereco"]
CPF_REGEX = re.compile(r"^[0-9]{11}$")
VALID_STATUS = {"ativo", "inativo"}


def validar_documento(doc):
    """
    Retorna uma lista de mensagens de erro para o documento informado.
    Se a lista vier vazia, o doc estaria ok para o jsonSchema atual.
    """
    erros = []

    # Campos obrigatórios
    for campo in REQUIRED_FIELDS:
        if campo not in doc:
            erros.append(f"Campo obrigatório ausente: {campo}")

    # CPF
    cpf = doc.get("cpf")
    if cpf is not None:
        if not isinstance(cpf, str):
            erros.append(f"cpf não é string (tipo={type(cpf).__name__})")
        elif not CPF_REGEX.match(cpf):
            erros.append(f"cpf não bate com regex de 11 dígitos: {cpf!r}")

    # Status
    status = doc.get("status")
    if status is not None and status not in VALID_STATUS:
        erros.append(
            f"status inválido: {status!r} (esperado: {sorted(VALID_STATUS)})"
        )

    # Endereco deve ser objeto/dict
    if "endereco" in doc and not isinstance(doc["endereco"], dict):
        erros.append(
            f"endereco não é objeto/dict (tipo={type(doc['endereco']).__name__})"
        )

    return erros


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    total = 0
    com_erro = 0
    exemplos = []

    try:
        print(f"Analisando documentos da coleção: {col.name!r} (db={col.database.name!r})\n")

        # Ignora soft-deletados
        filtro = {
            "$or": [
                {"marcado_para_exclusao": {"$exists": False}},
                {"marcado_para_exclusao": False},
            ]
        }

        for doc in col.find(filtro):
            total += 1
            erros = validar_documento(doc)

            if erros:
                com_erro += 1
                if len(exemplos) < 20:
                    exemplos.append(
                        {
                            "_id": str(doc.get("_id")),
                            "cpf": doc.get("cpf"),
                            "status": doc.get("status"),
                            "erros": erros,
                        }
                    )

        print("===== RESUMO DA ANÁLISE =====")
        print(f"Total de documentos analisados (ignorando marcados_para_exclusao): {total}")
        print(f"Documentos que violariam o jsonSchema atual: {com_erro}")

        if exemplos:
            print("\nAlguns exemplos de documentos problemáticos (até 20):")
            for ex in exemplos:
                pprint(ex)
                print("-" * 40)

        print(
            "\n✅ Análise concluída. Nenhuma alteração foi feita no banco.\n"
            "Use este relatório para planejar correções/migrações de dados com segurança."
        )

    finally:
        client.close()
        print("Conexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
