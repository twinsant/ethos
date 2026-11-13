#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ETHOS_ENV_FILE:-$ROOT/ops/production.env}"
INVENTORY="${ANSIBLE_INVENTORY:-$ROOT/../twinsant.com/ops/ansible/inventory.ini}"
HOSTS="${ETHOS_ANSIBLE_HOSTS:-app}"
CERTIFICATE_ID="${ETHOS_CERTIFICATE_ID:-bf3pwcJF}"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    printf 'Usage: bash ops/deploy.sh\n\n'
    printf 'Configure ops/production.env, then commit and push the release to origin/main.\n'
    printf 'Overrides: ETHOS_ENV_FILE, ETHOS_ABI_DIR, ANSIBLE_INVENTORY, ETHOS_ANSIBLE_HOSTS,\n'
    printf '           ETHOS_CERTIFICATE_ID.\n'
    exit 0
fi
if [[ $# -ne 0 ]]; then
    printf 'Unexpected argument. Run bash ops/deploy.sh --help.\n' >&2
    exit 1
fi

for command in ansible-playbook ansible-inventory openssl python3 shasum cut tccli uv git; do
    if ! command -v "$command" >/dev/null 2>&1; then
        printf 'Required command not found: %s\n' "$command" >&2
        exit 1
    fi
done

if [[ ! -f "$ENV_FILE" ]]; then
    printf 'Production environment file not found: %s\n' "$ENV_FILE" >&2
    printf 'Copy ops/production.env.example and configure it first.\n' >&2
    exit 1
fi

if [[ ! -f "$INVENTORY" ]]; then
    printf 'Ansible inventory not found: %s\n' "$INVENTORY" >&2
    printf 'Set ANSIBLE_INVENTORY to an inventory containing the target host.\n' >&2
    exit 1
fi

set -a
# This file is a shell-compatible environment file; keep secrets out of CLI arguments.
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${ENDPOINT:?Set ENDPOINT in the production environment file}"
: "${ETHOS_COOKIE_SECRET:?Set ETHOS_COOKIE_SECRET in the production environment file}"
: "${WALLETCONNECT_PROJECT_ID:?Set WALLETCONNECT_PROJECT_ID in the production environment file}"
if [[ ${#ETHOS_COOKIE_SECRET} -lt 32 || "$ETHOS_COOKIE_SECRET" == replace-* || "$ETHOS_COOKIE_SECRET" == __TODO:* ]]; then
    printf 'ETHOS_COOKIE_SECRET must be a non-placeholder secret of at least 32 characters.\n' >&2
    exit 1
fi

if [[ "$(git -C "$ROOT" branch --show-current)" != "main" ]]; then
    printf 'Deploy from the main branch after pushing the release commit.\n' >&2
    exit 1
fi

git -C "$ROOT" fetch --quiet origin main
COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
REMOTE_COMMIT="$(git -C "$ROOT" rev-parse origin/main)"
if [[ "$COMMIT" != "$REMOTE_COMMIT" ]]; then
    printf 'Local HEAD must match origin/main before deploying.\n' >&2
    exit 1
fi
if [[ -n "$(git -C "$ROOT" status --porcelain)" ]]; then
    printf 'Commit or stash all EthOS worktree changes before deploying.\n' >&2
    exit 1
fi

umask 077
TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ethos-deploy.XXXXXXXX")"
chmod 700 "$TEMP_DIR"
cleanup() {
    local status=$?
    rm -f "$TEMP_DIR/requirements.txt" "$TEMP_DIR/extra-vars.json" \
        "$TEMP_DIR/certificate/server.crt" "$TEMP_DIR/certificate/server.key"
    if [[ -d "$TEMP_DIR/certificate" ]]; then
        rmdir "$TEMP_DIR/certificate"
    fi
    rmdir "$TEMP_DIR"
    return "$status"
}
trap cleanup EXIT
ABI_ROOT="${ETHOS_ABI_DIR:-$ROOT/ops/abi}"
CHAIN_ID="$(python3 "$ROOT/ops/check-contracts.py" "$ABI_ROOT")"
printf 'RPC and deployed contracts verified for chain %s.\n' "$CHAIN_ID"
uv export --project "$ROOT" --locked --no-dev --format requirements-txt --no-header --no-annotate \
    --output-file "$TEMP_DIR/requirements.txt" >/dev/null
chmod 600 "$TEMP_DIR/requirements.txt"

python3 "$ROOT/ops/download-tencent-certificate.py" \
    "$CERTIFICATE_ID" "$TEMP_DIR/certificate"
openssl x509 -in "$TEMP_DIR/certificate/server.crt" -noout \
    -checkhost meta.twinsant.com -checkend 86400 >/dev/null
CERT_PUBLIC_KEY="$(
    openssl x509 -in "$TEMP_DIR/certificate/server.crt" -pubkey -noout |
        openssl pkey -pubin -outform DER |
        shasum -a 256 | cut -d ' ' -f 1
)"
PRIVATE_PUBLIC_KEY="$(
    openssl pkey -in "$TEMP_DIR/certificate/server.key" -pubout -outform DER |
        shasum -a 256 | cut -d ' ' -f 1
)"
if [[ "$CERT_PUBLIC_KEY" != "$PRIVATE_PUBLIC_KEY" ]]; then
    printf 'Downloaded TLS certificate and private key do not match.\n' >&2
    exit 1
fi

ansible-inventory -i "$INVENTORY" --list >/dev/null
python3 - "$TEMP_DIR/extra-vars.json" "$COMMIT" "$ENV_FILE" "$TEMP_DIR" "$HOSTS" "$ROOT" "$ABI_ROOT" "$CHAIN_ID" <<'PY'
import json
import os
import sys

path, commit, env_file, temp_dir, hosts, root, abi_root, chain_id = sys.argv[1:]
with open(path, "w", encoding="utf-8") as output:
    json.dump({
        "ethos_commit": commit,
        "ethos_env_file": os.path.abspath(env_file),
        "ethos_temp_dir": temp_dir,
        "ethos_hosts": hosts,
        "ethos_local_root": root,
        "ethos_abi_root": os.path.abspath(abi_root),
        "ethos_chain_id": chain_id,
    }, output)
PY
chmod 600 "$TEMP_DIR/extra-vars.json"

ansible-playbook -i "$INVENTORY" "$ROOT/ops/ansible/deploy.yml" \
    --extra-vars "@$TEMP_DIR/extra-vars.json"
