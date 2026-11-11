#!/usr/bin/env python3
"""Validate an existing RPC chain and the deployed Player contract."""
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def rpc(endpoint, method, params):
    request = Request(
        endpoint,
        data=json.dumps({
            "jsonrpc": "2.0", "method": method, "params": params, "id": 1,
        }).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "EthOS/1.0"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except (OSError, ValueError, URLError) as error:
        raise RuntimeError(f"RPC {method} failed; check ENDPOINT and network access") from error
    if not isinstance(payload, dict) or "error" in payload or "result" not in payload:
        raise RuntimeError(f"RPC {method} returned an error or invalid response")
    return payload["result"]


def check_contracts(abi_root):
    endpoint = os.environ.get("ENDPOINT", "")
    if urlsplit(endpoint).scheme not in ("http", "https"):
        raise ValueError("ENDPOINT must be an HTTP(S) JSON-RPC URL")
    chain_hex = rpc(endpoint, "eth_chainId", [])
    if not isinstance(chain_hex, str) or not re.fullmatch(r"0x[0-9a-fA-F]+", chain_hex):
        raise ValueError("RPC eth_chainId returned an invalid chain ID")
    chain_id = str(int(chain_hex, 16))
    if chain_id in ("1337", "31337"):
        raise ValueError("Production deployment refuses ephemeral Hardhat development chains")
    for name in ("Player",):
        abi_path = Path(abi_root) / chain_id / f"{name}.json"
        try:
            contract = json.loads(abi_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise ValueError(f"Missing or invalid ABI: {abi_path}") from error
        if (
            not isinstance(contract, dict)
            or not isinstance(contract.get("abi"), list)
            or not contract["abi"]
            or not isinstance(contract.get("address"), str)
            or not re.fullmatch(r"0x[0-9a-fA-F]{40}", contract["address"])
        ):
            raise ValueError(f"Invalid ABI or address: {abi_path}")
        code = rpc(endpoint, "eth_getCode", [contract["address"], "latest"])
        if (
            not isinstance(code, str)
            or not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})+", code)
            or not any(character != "0" for character in code[2:])
        ):
            raise ValueError(f"{name} has no deployed bytecode on chain {chain_id}")
    return chain_id


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: check-contracts.py ABI_ROOT")
    try:
        print(check_contracts(sys.argv[1]))
    except (ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from None
