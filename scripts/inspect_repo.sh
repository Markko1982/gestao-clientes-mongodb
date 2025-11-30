#!/usr/bin/env bash
set -euo pipefail

# Zera/Cria o relatório
: > repo_scan.txt

{
  echo "# Repo overview"
  echo "## Top-level (ls -la)"
  ls -la

  echo
  echo "## Shallow tree (maxdepth=2, oculta pastas pesadas)"
  find . -maxdepth 2 \
    -type d \( -path '*/.git' -o -path '*/node_modules' -o -path '*/target' -o -path '*/build' \) -prune -o \
    -print

  echo
  echo "## MongoDB URIs encontradas"
  (grep -RIn \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=target --exclude-dir=build \
    -E 'mongodb(\+srv)?:\/\/' . || true)

  echo
  echo "## Arquivos que mencionam Mongo (pymongo, Spring Data, mongoose)"
  (grep -RIl \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=target --exclude-dir=build \
    -E 'Mongo|pymongo|spring\.data\.mongodb|mongoose' . | sed 's/^/ - /' || true)

  echo
  echo "## docker-compose e .env"
  (ls -1 docker-compose*.yml 2>/dev/null | sed 's/^/ - /' || true)
  (ls -1 .env* 2>/dev/null | sed 's/^/ - /' || true)
} >> repo_scan.txt

echo "Relatório gerado em repo_scan.txt"
