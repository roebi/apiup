"""
OpenAPI spec loading and route extraction.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_METHODS = ("get", "post", "put", "patch", "delete", "head", "options")


@dataclass
class Route:
    method: str  # uppercase: GET, POST, ...
    path: str  # e.g. /items/{id}
    summary: str
    operation_id: str
    responses: dict[str, Any]


def load_spec(spec_path: str) -> dict[str, Any]:
    """Load and minimally validate an OpenAPI 3.x spec from YAML or JSON."""
    path = Path(spec_path)

    if not path.exists():
        print(f"ERROR: Spec file not found: {spec_path}", file=sys.stderr)
        print(
            "Tip: place your spec at ~/.openapi/spec.yaml or use --spec PATH",
            file=sys.stderr,
        )
        sys.exit(1)

    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
            sys.exit(2)
        with open(path) as f:
            spec: dict[str, Any] = yaml.safe_load(f) or {}
    elif path.suffix == ".json":
        with open(path) as f:
            spec = json.load(f)
    else:
        print(
            f"ERROR: Unsupported spec format '{path.suffix}'. Use .yaml or .json",
            file=sys.stderr,
        )
        sys.exit(1)

    if "paths" not in spec:
        print("ERROR: Spec has no 'paths' section.", file=sys.stderr)
        sys.exit(1)

    return spec


def extract_routes(spec: dict[str, Any]) -> list[Route]:
    """Return all HTTP routes defined in the spec."""
    routes: list[Route] = []
    for path, path_item in spec.get("paths", {}).items():
        for method in SUPPORTED_METHODS:
            op = path_item.get(method)
            if op is None:
                continue
            routes.append(
                Route(
                    method=method.upper(),
                    path=path,
                    summary=op.get("summary", ""),
                    operation_id=op.get("operationId", ""),
                    responses=op.get("responses", {}),
                )
            )
    return routes


def spec_info(spec: dict[str, Any]) -> tuple[str, str]:
    """Return (title, version) from spec info block."""
    info = spec.get("info", {})
    return info.get("title", "apiup mock server"), info.get("version", "?")
