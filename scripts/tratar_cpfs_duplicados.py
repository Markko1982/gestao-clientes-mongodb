"""
Trata CPFs duplicados após normalização.

Regra:
- Para cada CPF normalizado:
  - mantém 1 documento principal;
  - os demais recebem:
      status = "inativo"
      marcado_para_exclusao = True
      cpf_principal_id = <_id do principal>
"""

import re
from datetime import datetime
from pprint import pprint

from bson.objectid import ObjectId
from pymongo.errors import WriteError
from config import get_collection

DRY_RUN = False  # ✅ agora APLICA as alterações

def normalizar_cpf(cpf_str):
    if not isinstance(cpf_str, str):
        return None
    apenas_digitos = re.sub(r"\D", "", cpf_str or "")
    if len(apenas_digitos) != 11:
        return None
    return apenas_digitos


def _get_timestamp(doc):
    """
    Tenta usar data_cadastro, senão usa o timestamp embutido no ObjectId.
    """
    dt = doc.get("data_cadastro")
    if isinstance(dt, datetime):
        return dt

    _id = doc.get("_id")
    if isinstance(_id, ObjectId):
        return _id.generation_time

    # fallback: agora
    return datetime.utcnow()


def escolher_principal(docs):
    """
    Escolhe o documento principal dentro de um grupo com mesmo CPF normalizado.
    Regra:
      1) Preferir status == 'ativo'
      2) Dentro do grupo escolhido, pegar o mais recente (timestamp maior)
    """
    if not docs:
        return None

    ativos = [d for d in docs if d.get("status") == "ativo"]
    candidatos = ativos if ativos else docs

    # escolhe o mais recente por timestamp
    principal = max(candidatos, key=_get_timestamp)
    return principal


def main():
    bundle = get_collection()
    col = bundle.collection
    client = bundle.client

    try:
        print(f"Coleção: {col.name!r} (db={col.database.name!r})")
        print(f"DRY_RUN = {DRY_RUN}\n")

        mapa = {}
        total_analisados = 0

        # Monta mapa cpf_normalizado -> lista de docs
        for doc in col.find({"cpf": {"$type": "string"}}):
            total_analisados += 1
            cpf_original = doc.get("cpf")
            cpf_norm = normalizar_cpf(cpf_original)
            if not cpf_norm:
                continue

            mapa.setdefault(cpf_norm, []).append(doc)

        # Filtra apenas CPFs com mais de um documento
        duplicados = {k: v for k, v in mapa.items() if len(v) > 1}

        print("===== RESUMO INICIAL =====")
        print(f"Total de documentos analisados (cpf string): {total_analisados}")
        print(f"Total de CPFs normalizados distintos: {len(mapa)}")
        print(f"Total de CPFs com duplicidade: {len(duplicados)}\n")

        total_para_marcar = 0
        total_atualizados = 0
        exemplos = []

        for cpf_norm, docs in duplicados.items():
            principal = escolher_principal(docs)
            if not principal:
                continue

            principal_id = principal["_id"]

            # todos menos o principal serão marcados
            secundarios = [d for d in docs if d["_id"] != principal_id]
            total_para_marcar += len(secundarios)

            # guarda alguns exemplos
            if len(exemplos) < 10:
                exemplos.append(
                    {
                        "cpf_normalizado": cpf_norm,
                        "principal": {
                            "_id": str(principal_id),
                            "cpf": principal.get("cpf"),
                            "status": principal.get("status"),
                        },
                        "secundarios": [
                            {
                                "_id": str(d["_id"]),
                                "cpf": d.get("cpf"),
                                "status": d.get("status"),
                            }
                            for d in secundarios
                        ],
                    }
                )

            # Aplica updates nos secundários
            for d in secundarios:
                try:
                    res = col.update_one(
                        {"_id": d["_id"]},
                        {
                            "$set": {
                                "status": "inativo",
                                "marcado_para_exclusao": True,
                                "cpf_principal_id": principal_id,
                            }
                        },
                    )
                    if res.modified_count == 1:
                        total_atualizados += 1
                except WriteError as e:
                    print(f"❌ Falha ao atualizar documento {d.get('_id')}:")
                    pprint(getattr(e, "details", str(e)))

        print("===== RESUMO FINAL =====")
        print(f"Total de CPFs com duplicidade: {len(duplicados)}")
        print(f"Total de documentos a marcar como duplicados: {total_para_marcar}")
        print(f"✅ Atualizações realizadas (marcados para exclusão): {total_atualizados}")

        if exemplos:
            print("\nAlguns exemplos de grupos (principal x secundários):")
            for ex in exemplos:
                pprint(ex)
                print("-" * 60)

    finally:
        client.close()
        print("\nConexão com o MongoDB fechada.")


if __name__ == "__main__":
    main()
