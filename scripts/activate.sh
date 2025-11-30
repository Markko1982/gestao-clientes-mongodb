#!/usr/bin/env bash

if [ -f ".venv/bin/activate" ]; then
  VENV=".venv"
elif [ -f ".venv_path" ] && [ -d "$(cat .venv_path)/bin" ]; then
  VENV="$(cat .venv_path)"
else
  echo "✗ Nenhum venv encontrado. Rode: ./scripts/setup_env.sh"
  exit 1
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "✅ Venv ativado: $VENV"
python -V
pip list | grep -E 'pymongo|python-dotenv' || true
