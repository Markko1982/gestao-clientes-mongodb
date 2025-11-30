#!/usr/bin/env bash
set -euo pipefail

PY=${PY:-python3}

create_local_venv() {
  echo ">> Tentando criar ambiente virtual local .venv (com --copies)..."
  $PY -m venv --copies .venv
  echo ">> Ativando .venv local"
  # shellcheck disable=SC1091
  source .venv/bin/activate
}

create_home_venv() {
  VHOME="$HOME/.venvs/gestao-clientes-mongodb"
  echo ">> Criando ambiente em $VHOME (fallback)"
  mkdir -p "$HOME/.venvs"
  $PY -m venv --copies "$VHOME"
  # shellcheck disable=SC1091
  source "$VHOME/bin/activate"
  echo "$VHOME" > .venv_path 2>/dev/null || true
}

echo ">> Verificando disponibilidade do módulo venv"
$PY -c "import venv" 2>/dev/null || {
  echo "✗ Python venv não disponível. Instale: sudo apt-get install -y python3-venv"
  exit 1
}

# Tenta local primeiro; se falhar, usa home
if create_local_venv 2>/dev/null; then
  WHERE=".venv"
else
  echo ">> Falhou criar .venv local (provável filesystem sem symlink). Indo para fallback..."
  create_home_venv
  WHERE="$(cat .venv_path 2>/dev/null || true)"
fi

echo ">> Atualizando pip"
pip install --upgrade pip

if [ -f requirements.txt ]; then
  echo ">> Instalando dependências de requirements.txt"
  pip install -r requirements.txt
else
  echo ">> requirements.txt não encontrado, instalando pacotes essenciais"
  pip install pymongo python-dotenv
fi

echo
echo "✅ Ambiente pronto em: ${WHERE:-$HOME/.venvs/gestao-clientes-mongodb}"
echo "✅ Para ativar depois:"
if [ "${WHERE:-}" = ".venv" ]; then
  echo "   source .venv/bin/activate"
else
  echo "   source \"$(cat .venv_path)\"/bin/activate"
fi

echo "✅ Python: $(python -V)"
echo "✅ Pacotes instalados (trecho):"
pip list | grep -E 'pymongo|python-dotenv' || true
