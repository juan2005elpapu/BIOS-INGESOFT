#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if ! command -v python >/dev/null 2>&1; then
  echo "Python 3 es requerido en el PATH."
  exit 1
fi

if [ ! -d "$PROJECT_ROOT/.venv" ]; then
  python -m venv "$PROJECT_ROOT/.venv"
fi

# shellcheck disable=SC1091
source "$PROJECT_ROOT/.venv/bin/activate"

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py test