#!/usr/bin/env python3
"""Convert Geometry Dash local saves between Windows and macOS formats."""

from __future__ import annotations

import argparse
import base64
import gzip
import os
from pathlib import Path
import platform
import subprocess
import tempfile


MAC_KEY_HEX = "69707539545576353479765d6973464d6835403b742e3577333445325279407b"
MAC_KEY = bytes.fromhex(MAC_KEY_HEX)
WINDOWS_XOR_KEY = 0x0B


def _validate_xml(xml: bytes) -> bytes:
    if not xml.startswith(b"<?xml"):
        raise ValueError("decoded data is not Geometry Dash XML")
    return xml


def _openssl_ecb(data: bytes, decrypt: bool) -> bytes:
    with tempfile.TemporaryDirectory(prefix="gd-save-converter-") as directory:
        source = Path(directory) / "input"
        output = Path(directory) / "output"
        source.write_bytes(data)
        command = [
            "openssl",
            "enc",
            "-aes-256-ecb",
            "-K",
            MAC_KEY_HEX,
            "-nopad",
            "-in",
            str(source),
            "-out",
            str(output),
        ]
        if decrypt:
            command.insert(2, "-d")
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode:
            message = result.stderr.strip() or "openssl failed"
            raise RuntimeError(message)
        return output.read_bytes()


def _pycryptodome_ecb(data: bytes, decrypt: bool) -> bytes:
    try:
        from Crypto.Cipher import AES
    except ImportError as exc:
        raise RuntimeError(
            "PyCryptodome is required for AES operations when OpenSSL is unavailable. "
            "Install it with: python3 -m pip install -r requirements.txt"
        ) from exc
    cipher = AES.new(MAC_KEY, AES.MODE_ECB)
    return cipher.decrypt(data) if decrypt else cipher.encrypt(data)


def _mac_ecb(data: bytes, decrypt: bool) -> bytes:
    if platform.system() == "Darwin":
        try:
            return _openssl_ecb(data, decrypt)
        except (FileNotFoundError, OSError):
            pass
    return _pycryptodome_ecb(data, decrypt)


def decrypt_windows(data: bytes) -> bytes:
    try:
        decoded = base64.urlsafe_b64decode(
            bytes(byte ^ WINDOWS_XOR_KEY for byte in data)
        )
        return _validate_xml(gzip.decompress(decoded))
    except (ValueError, EOFError, gzip.BadGzipFile, base64.binascii.Error) as exc:
        raise ValueError("input is not a valid Windows Geometry Dash save") from exc


def encrypt_windows(xml: bytes) -> bytes:
    compressed = gzip.compress(_validate_xml(xml))
    encoded = base64.urlsafe_b64encode(compressed)
    return bytes(byte ^ WINDOWS_XOR_KEY for byte in encoded)


def decrypt_mac(data: bytes) -> bytes:
    if not data or len(data) % 16:
        raise ValueError("input is not a valid macOS Geometry Dash save")
    decrypted = _mac_ecb(data, decrypt=True)
    padding = decrypted[-1]
    if not 1 <= padding <= 16 or decrypted[-padding:] != bytes([padding]) * padding:
        raise ValueError("macOS save has invalid padding")
    return _validate_xml(decrypted[:-padding])


def encrypt_mac(xml: bytes) -> bytes:
    xml = _validate_xml(xml)
    padding = 16 - (len(xml) % 16)
    return _mac_ecb(xml + bytes([padding]) * padding, decrypt=False)


def convert(source: Path, source_format: str) -> None:
    backup = source.with_name(f"{source.name}.backup")
    if backup.exists():
        raise FileExistsError(f"{backup} already exists; remove it before converting")
    data = source.read_bytes()
    xml = decrypt_windows(data) if source_format == "windows" else decrypt_mac(data)
    converted = (
        encrypt_mac(xml) if source_format == "windows" else encrypt_windows(xml)
    )
    temporary = source.with_name(f".{source.name}.tmp")
    temporary.write_bytes(converted)
    try:
        backup.write_bytes(data)
        os.replace(temporary, source)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Converted {source} in place; backup: {backup}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert Geometry Dash saves between Windows and macOS formats."
    )
    parser.add_argument("source", type=Path, help="input .dat file")
    parser.add_argument(
        "--from",
        dest="source_format",
        choices=("windows", "macos"),
        required=True,
        help="format of the input file",
    )
    args = parser.parse_args()
    try:
        convert(args.source, args.source_format)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
