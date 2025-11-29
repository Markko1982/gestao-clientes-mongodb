"""
APLICA de fato a migração de CPFs formatados
(ex.: '870.125.694-76') para o padrão '87012569476'.

⚠ ESTE SCRIPT ALTERA DOCUMENTOS NA COLEÇÃO 'clientes'.

Pré-requisitos:
- Backup recente da coleção (ok).
- DRY RUN já executado e conferido (ok).

Regras:
- Apenas documentos com cpf string são analisados.
- Remove tudo que não for dígito.
- Se após limpar tiver exatamente 11 dígitos, faz update.
"""

import re
from pprint import pprint
from pymongo.errors import WriteError
from config import get_collection

APLICAR_ALTERACOES = True  # 👈 Aqui é SEMPRE verdadeiro

CPF_REGEX_TARGET = re.compile(r"^[0-9]{11}$")


def normalizar_cpf(cpf_str: str) -> str | None:
    """
    Remove caracteres não numéricos.
    Se não resultar em exatamente 11 dígitos, retorna None.
    """
    if not isinstance(cpf_str, str):
        return None

    apenas_digitos = re.sub(r"\D", "", cpf_str or "")
    if len(apenas_digitos) != 11:
        return None
    return apenas_digitos


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    try:
        print(f"Coleção: {col.name!r} (db={col.database.name!r})")
        print("⚠ APLICAR_ALTERACOES = True → ESTE SCRIPT VAI FAZER UPDATES\n")
        print("Buscando documentos com cpf string...\n")

        filtro = {"cpf": {"$type": "string"}}

        total_analisados = 0
        candidatos = 0
        atualizados = 0
        ignorados = 0
        exemplos = []

        for doc in col.find(filtro):
            total_analisados += 1
            cpf_original = doc.get("cpf")
            novo_cpf = normalizar_cpf(cpf_original)

            # Se não conseguimos normalizar ou já está ok, ignoramos
            if not novo_cpf or novo_cpf == cpf_original:
                ignorados += 1
                continue

            candidatos += 1

            if len(exemplos) < 10:
                exemplos.append(
                    {
                        "_id": str(doc.get("_id")),
                        "cpf_original": cpf_original,
                        "cpf_normalizado": novo_cpf,
                    }
                )

            # Migração real
            try:
                res = col.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"cpf": novo_cpf}},
                )
                if res.modified_count == 1:
                    atualizados += 1
            except WriteError as e:
                print(f"❌ Falha ao atualizar documento {doc.get('_id')}:")
                pprint(getattr(e, "details", str(e)))

        print("\n===== RESUMO DA MIGRAÇÃO DE CPFs (APLICADA) =====")
        print(f"Total analisados (cpf string): {total_analisados}")
        print(f"Candidatos a normalização: {candidatos}")
        print(f"Documentos ignorados/sem mudança: {ignorados}")
        print(f"✅ Atualizações realizadas: {atualizados}")

        if exemplos:
            print("\nAlguns exemplos de normalização de CPF aplicadas:")
            for ex in exemplos:
                pprint(ex)
                print("-" * 40)

    finally:
        client.close()
        print("\nConexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
