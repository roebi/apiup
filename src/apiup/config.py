"""
Config resolution for apiup.

Convention:
    ~/.openapi/spec.json      — default OpenAPI spec (JSON)
    ~/.openapi/spec.yaml      — default OpenAPI spec (YAML, checked second)
    ~/.openapi/config.yaml    — optional defaults (port, host, mode, spec)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_DIR: Path = Path.home() / ".openapi"
DEFAULT_CONFIG: Path = DEFAULT_CONFIG_DIR / "config.yaml"

# Auto-detection order: spec.json first, then spec.yaml
DEFAULT_SPEC_CANDIDATES: list[Path] = [
    DEFAULT_CONFIG_DIR / "spec.json",
    DEFAULT_CONFIG_DIR / "spec.yaml",
]


def _default_spec() -> str:
    """Return first existing default spec, or spec.json as the canonical fallback."""
    for candidate in DEFAULT_SPEC_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return str(DEFAULT_SPEC_CANDIDATES[0])


@dataclass
class ApiupConfig:
    spec: str = field(default_factory=_default_spec)
    port: int = 8080
    host: str = "127.0.0.1"
    mode: str = "mock"


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        print(
            "ERROR: pyyaml not installed. Run: pip install pyyaml",
            file=sys.stderr,
        )
        sys.exit(2)
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_config(
    spec: str | None = None,
    port: int | None = None,
    host: str | None = None,
    mode: str | None = None,
) -> ApiupConfig:
    """Resolve config from file + CLI overrides.

    Precedence: CLI args > ~/.openapi/config.yaml > auto-detected default > spec.json fallback.
    """
    cfg = ApiupConfig()

    if DEFAULT_CONFIG.exists():
        file_cfg = _load_yaml(DEFAULT_CONFIG)
        if "spec" in file_cfg and file_cfg["spec"]:
            cfg.spec = str(Path(str(file_cfg["spec"])).expanduser())
        if "port" in file_cfg and file_cfg["port"]:
            cfg.port = int(file_cfg["port"])
        if "host" in file_cfg and file_cfg["host"]:
            cfg.host = str(file_cfg["host"])
        if "mode" in file_cfg and file_cfg["mode"]:
            cfg.mode = str(file_cfg["mode"])

    # CLI overrides
    if spec is not None:
        cfg.spec = str(Path(spec).expanduser())
    if port is not None:
        cfg.port = port
    if host is not None:
        cfg.host = host
    if mode is not None:
        cfg.mode = mode

    # Always expand ~ in spec path
    cfg.spec = str(Path(cfg.spec).expanduser())

    return cfg
