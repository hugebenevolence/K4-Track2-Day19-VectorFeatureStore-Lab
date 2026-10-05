"""Switch .env between the two supported lab stacks."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"


def select(mode: str) -> None:
    values = {
        "lite": {
            "QDRANT_MODE": "memory", "EMBEDDING_BACKEND": "fastembed",
            "FEAST_ONLINE_STORE": "sqlite", "FEAST_OFFLINE_STORE": "file",
        },
        "docker": {
            "QDRANT_MODE": "server", "EMBEDDING_BACKEND": "bge-m3",
            "FEAST_ONLINE_STORE": "redis", "FEAST_OFFLINE_STORE": "postgres",
        },
    }[mode]
    body = ENV.read_text(encoding="utf-8") if ENV.exists() else (ROOT / ".env.example").read_text(encoding="utf-8")
    for key, value in values.items():
        pattern = rf"^{key}=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, body, flags=re.MULTILINE):
            body = re.sub(pattern, replacement, body, count=1, flags=re.MULTILINE)
        else:
            body += f"\n{replacement}"
    ENV.write_text(body, encoding="utf-8")
    print(f"Selected {mode} in {ENV}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["lite", "docker"])
    select(parser.parse_args().mode)
