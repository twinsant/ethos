#!/usr/bin/env python3
import base64
import binascii
import json
import os
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from subprocess import run


def run_tccli(*arguments):
    result = run(
        ["tccli", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(f"Tencent Cloud CLI failed with exit code {result.returncode}")
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise RuntimeError("Tencent Cloud returned an invalid response")
    return payload.get("Response", payload)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: download-tencent-certificate.py CERTIFICATE_ID OUTPUT_DIR")

    certificate_id, output_dir = sys.argv[1:]
    metadata = run_tccli("ssl", "DescribeCertificate", "--CertificateId", certificate_id)
    if metadata.get("CertificateId") != certificate_id or str(metadata.get("Status")) != "1":
        raise RuntimeError("The requested Tencent Cloud certificate is not issued")

    download = run_tccli("ssl", "DownloadCertificate", "--CertificateId", certificate_id)
    archive_bytes = base64.b64decode(download["Content"], validate=True)
    output_path = Path(output_dir)
    output_path.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(output_path, 0o700)

    with zipfile.ZipFile(BytesIO(archive_bytes)) as archive:
        candidates = []
        for entry in archive.infolist():
            if entry.file_size > 20_000_000:
                raise RuntimeError("Certificate archive contains an unexpectedly large file")
            name = Path(entry.filename).name.lower()
            if not name or entry.is_dir():
                continue
            content = archive.read(entry)
            if b"-----BEGIN CERTIFICATE-----" in content:
                candidates.append(("certificate", name, content))
            elif b"PRIVATE KEY-----" in content and b"-----BEGIN " in content:
                candidates.append(("private_key", name, content))

    certificates = [item for item in candidates if item[0] == "certificate"]
    private_keys = [item for item in candidates if item[0] == "private_key"]
    if not certificates or not private_keys:
        raise RuntimeError("Certificate archive is missing a PEM certificate or private key")

    certificate = max(
        certificates,
        key=lambda item: ("bundle" in item[1] or "nginx" in item[1], len(item[2])),
    )[2]
    private_key = private_keys[0][2]
    for name, content in (("server.crt", certificate), ("server.key", private_key)):
        destination = output_path / name
        destination.write_bytes(content)
        os.chmod(destination, 0o600)

    print("Tencent Cloud certificate downloaded to a private temporary directory.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, binascii.Error, RuntimeError, zipfile.BadZipFile) as error:
        raise SystemExit(str(error)) from error
