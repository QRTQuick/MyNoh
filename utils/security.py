from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path

APP_SERVICE = "mynoh"


class SecretStore:
    """Keyring-first secret storage with encrypted local fallback."""

    def __init__(self, fallback_key_path: Path) -> None:
        self.fallback_key_path = fallback_key_path
        self.fallback_key_path.parent.mkdir(parents=True, exist_ok=True)

    def set_secret(self, key: str, value: str) -> None:
        try:
            import keyring
            keyring.set_password(APP_SERVICE, key, value)
            return
        except Exception:
            self._fallback_write(key, value)

    def get_secret(self, key: str) -> str:
        try:
            import keyring
            value = keyring.get_password(APP_SERVICE, key)
            if value:
                return value
        except Exception:
            pass
        return self._fallback_read(key)

    def _fernet(self):
        try:
            from cryptography.fernet import Fernet
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Install cryptography for encrypted fallback storage") from exc
        if not self.fallback_key_path.exists():
            raw = base64.urlsafe_b64encode(os.urandom(32))
            self.fallback_key_path.write_bytes(raw)
            try:
                os.chmod(self.fallback_key_path, 0o600)
            except OSError:
                pass
        return Fernet(self.fallback_key_path.read_bytes())

    def _file_for(self, key: str) -> Path:
        name = hashlib.sha256(key.encode()).hexdigest() + ".secret"
        return self.fallback_key_path.parent / name

    def _fallback_write(self, key: str, value: str) -> None:
        self._file_for(key).write_bytes(self._fernet().encrypt(value.encode()))

    def _fallback_read(self, key: str) -> str:
        path = self._file_for(key)
        if not path.exists():
            return ""
        return self._fernet().decrypt(path.read_bytes()).decode()
