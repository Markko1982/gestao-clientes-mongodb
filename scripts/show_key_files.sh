#!/usr/bin/env bash
set -euo pipefail

mask_uri() {
  sed -E 's#(mongodb(\+srv)?:\/\/[^:]+:)[^@]+@#\1***@#g'
}

show() {
  local f="$1"
  if [ -f "$f" ]; then
    echo -e "\n===== $f ====="
    awk 'NR<=400{print}' "$f" | mask_uri
  fi
}

show ./config.py
show ./docker-compose.yml
show ./docker-compose.yaml
show ./src/conexao.py
show ./src/cliente_model.py
show ./src/cliente_crud.py
show ./src/post_setup_indices.py
show ./src/debug_mongo.py

echo -e "\n(Exibição concluída)"
