"""Cryptographic primitives used by Pseudonymity."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from pathlib import Path

from pseudonymity.io import ensure_parent


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def hmac_token(value: str, key: bytes, namespace: str, length: int = 18) -> str:
    if not str(value).strip():
        return ""
    payload = f"{namespace}:{normalise(value)}".encode("utf-8")
    digest = hmac.new(key, payload, hashlib.sha256).digest()
    token = base64.b32encode(digest).decode("ascii").rstrip("=")[:length]
    return f"{namespace[:4].upper()}-{token}"


def deterministic_int(value: str, key: bytes, namespace: str, modulo: int) -> int:
    payload = f"{namespace}:{normalise(value)}".encode("utf-8")
    digest = hmac.new(key, payload, hashlib.sha256).digest()
    return int.from_bytes(digest[:8], "big") % modulo


def secret_bytes(secret_text: str) -> bytes:
    secret_text = secret_text.strip()
    if re.fullmatch(r"[0-9a-fA-F]{64}", secret_text):
        return bytes.fromhex(secret_text)
    return secret_text.encode("utf-8")


def load_or_create_secret(secret_env: str, key_file: Path, create_key: bool) -> tuple[bytes, str]:
    env_value = os.environ.get(secret_env)
    if env_value:
        return secret_bytes(env_value), f"environment:{secret_env}"

    if key_file.exists():
        return secret_bytes(key_file.read_text(encoding="utf-8")), f"file:{key_file}"

    if not create_key:
        raise RuntimeError(
            "No pseudonymisation key found. Set the environment variable "
            f"{secret_env}, provide --key-file, or pass --create-key for a demo key."
        )

    ensure_parent(key_file)
    generated = secrets.token_hex(32)
    key_file.write_text(generated + "\n", encoding="utf-8")
    try:
        key_file.chmod(0o600)
    except OSError:
        pass
    return bytes.fromhex(generated), f"file:{key_file} (created)"
