#!/usr/bin/env bash
set -euo pipefail

# Educational demonstration mode. Do not present synthetic model results as BBC results.
if [[ ! -f data/models/newsbot2.joblib ]]; then
  echo 'NEWSBOT MODE: training on the included synthetic demonstration data.'
  python train.py --demo
fi

exec gunicorn --bind "0.0.0.0:${PORT:-10000}" --workers 1 --threads 2 --timeout 180 app:app
