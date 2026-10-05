"""The two setup paths must produce compatible Feast and embedding settings."""
from __future__ import annotations

from scripts import configure_feast, select_mode


def test_switching_modes_preserves_custom_values_and_configures_feast(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=example\nQDRANT_MODE=memory  # old\n", encoding="utf-8")
    monkeypatch.setattr(select_mode, "ENV", env_file)

    select_mode.select("docker")
    active = dict(
        line.split("=", 1) for line in env_file.read_text(encoding="utf-8").splitlines() if "=" in line
    )
    assert active["OPENAI_API_KEY"] == "example"
    assert active["QDRANT_MODE"] == "server"
    assert active["EMBEDDING_BACKEND"] == "bge-m3"
    assert active["FEAST_OFFLINE_STORE"] == "postgres"

    config = configure_feast.build_config("docker")
    assert config["online_store"]["type"] == "redis"
    assert config["offline_store"]["type"] == "postgres"
    assert config["offline_store"]["database"] == "feast_offline"
    assert config["registry"] == "registry_docker.db"

    select_mode.select("lite")
    assert "FEAST_OFFLINE_STORE=file" in env_file.read_text(encoding="utf-8")
    assert configure_feast.build_config("lite")["online_store"]["type"] == "sqlite"
    assert configure_feast.build_config("lite")["registry"] == "registry.db"
