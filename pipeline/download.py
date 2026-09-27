"""Download the City's published source files once; later runs reuse the local copies."""

import hashlib
import urllib.request
from pathlib import Path

from . import config


def download(force: bool = False) -> dict[str, Path]:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, url in config.SOURCES.items():
        path = config.RAW_DIR / name
        if force or not path.exists():
            partial = path.with_name(path.name + ".part")
            with urllib.request.urlopen(url, timeout=300) as response, open(partial, "wb") as out:
                while chunk := response.read(1 << 20):
                    out.write(chunk)
            partial.replace(path)
        paths[name] = path
    return paths


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()
