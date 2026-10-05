"""Generate the active Feast config from .env (Lite or Docker)."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import config as _config  # noqa: E402,F401  -- load .env

DEST = ROOT / "app" / "feast_repo" / "feature_store.yaml"


def build_config(mode: str) -> dict:
    result = {
        "project": "lab19",
        "provider": "local",
        "registry": "registry_docker.db" if mode == "docker" else "registry.db",
        "entity_key_serialization_version": 3,
    }
    if mode == "lite":
        result["online_store"] = {"type": "sqlite", "path": "online_store.db"}
        result["offline_store"] = {"type": "file"}
    elif mode == "docker":
        redis_url = urlparse(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        postgres_url = urlparse(os.getenv(
            "POSTGRES_URL", "postgresql://feast:feast@localhost:5432/feast_offline"
        ))
        if redis_url.scheme != "redis" or postgres_url.scheme not in ("postgres", "postgresql"):
            raise ValueError("REDIS_URL and POSTGRES_URL must be Redis/PostgreSQL URLs")
        result["online_store"] = {
            "type": "redis", "connection_string": f"{redis_url.hostname}:{redis_url.port or 6379}"
        }
        result["offline_store"] = {
            "type": "postgres",
            "host": postgres_url.hostname,
            "port": postgres_url.port or 5432,
            "database": postgres_url.path.lstrip("/"),
            "user": unquote(postgres_url.username or ""),
            "password": unquote(postgres_url.password or ""),
            "db_schema": "public",
            "sslmode": "disable",
        }
    else:
        raise ValueError(f"Unknown mode: {mode}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["lite", "docker"])
    args = parser.parse_args()
    DEST.write_text(yaml.safe_dump(build_config(args.mode), sort_keys=False), encoding="utf-8")
    print(f"Feast {args.mode} config: {DEST}")


if __name__ == "__main__":
    main()
