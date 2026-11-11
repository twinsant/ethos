#!/usr/bin/env bash
set -euo pipefail

cd /opt/ethos
set -a
source /etc/ethos/ethos.env
set +a
export PYTHONPATH=/opt/ethos/src
export ETHOS_ADDRESS=127.0.0.1
export ETHOS_ORIGIN=https://meta.twinsant.com
exec /opt/ethos/.venv/bin/python /opt/ethos/src/ethos/main.py --port=4003
