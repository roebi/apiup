"""Tests for spec loading and route extraction."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from apiup.mock import extract_mock_response
from apiup.spec import extract_routes, load_spec, spec_info

# ── Fixtures ────────────────────────────────────────────────────────────────

MINIMAL_SPEC = {
    "openapi": "3.0.3",
    "info": {"title": "Test API", "version": "1.2.3"},
    "paths": {
        "/ping": {
            "get": {
                "summary": "Ping",
                "responses": {
                    "200": {"content": {"application/json": {"example": {"pong": True}}}}
                },
            }
        },
        "/items": {
            "get": {
                "summary": "List items",
                "responses": {"200": {"content": {"application/json": {"example": [{"id": 1}]}}}},
            },
            "post": {
                "summary": "Create item",
                "responses": {
                    "201": {"content": {"application/json": {"example": {"id": 2, "name": "new"}}}}
                },
            },
        },
        "/items/{id}": {
            "delete": {
                "summary": "Delete item",
                "responses": {"204": {"description": "Deleted"}},
            }
        },
    },
}


@pytest.fixture
def spec_file(tmp_path: Path) -> Path:
    path = tmp_path / "spec.yaml"
    path.write_text(yaml.dump(MINIMAL_SPEC))
    return path


# ── spec.py tests ────────────────────────────────────────────────────────────


def test_load_spec_yaml(spec_file: Path) -> None:
    spec = load_spec(str(spec_file))
    assert "paths" in spec


def test_spec_info() -> None:
    title, version = spec_info(MINIMAL_SPEC)
    assert title == "Test API"
    assert version == "1.2.3"


def test_extract_routes_count() -> None:
    routes = extract_routes(MINIMAL_SPEC)
    assert len(routes) == 4


def test_extract_routes_methods() -> None:
    routes = extract_routes(MINIMAL_SPEC)
    methods = {r.method for r in routes}
    assert methods == {"GET", "POST", "DELETE"}


def test_extract_routes_paths() -> None:
    routes = extract_routes(MINIMAL_SPEC)
    paths = {r.path for r in routes}
    assert "/ping" in paths
    assert "/items/{id}" in paths


# ── mock.py tests ────────────────────────────────────────────────────────────


def test_mock_get_ping() -> None:
    route = next(r for r in extract_routes(MINIMAL_SPEC) if r.path == "/ping")
    status, body = extract_mock_response(route.responses, MINIMAL_SPEC)
    assert status == 200
    assert body == {"pong": True}


def test_mock_post_items() -> None:
    route = next(r for r in extract_routes(MINIMAL_SPEC) if r.method == "POST")
    status, body = extract_mock_response(route.responses, MINIMAL_SPEC)
    assert status == 201
    assert body["id"] == 2


def test_mock_delete_204() -> None:
    route = next(r for r in extract_routes(MINIMAL_SPEC) if r.method == "DELETE")
    status, body = extract_mock_response(route.responses, MINIMAL_SPEC)
    assert status == 204
    assert body is None


def test_mock_no_example_returns_stub() -> None:
    responses: dict = {"200": {"description": "OK"}}
    status, body = extract_mock_response(responses, {})
    assert status == 200
    assert body.get("_mock") is True


def test_load_spec_missing_file() -> None:
    with pytest.raises(SystemExit):
        load_spec("/nonexistent/path/spec.yaml")


# ── config.py tests ──────────────────────────────────────────────────────────

def test_default_spec_prefers_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """spec.json is picked over spec.yaml when both exist."""
    import apiup.config as cfg_mod

    openapi_dir = tmp_path / ".openapi"
    openapi_dir.mkdir()
    (openapi_dir / "spec.json").write_text('{"openapi":"3.0.3","info":{"title":"T","version":"1"},"paths":{}}')
    (openapi_dir / "spec.yaml").write_text("openapi: 3.0.3\ninfo:\n  title: T\n  version: '1'\npaths: {}")

    monkeypatch.setattr(cfg_mod, "DEFAULT_CONFIG_DIR", openapi_dir)
    monkeypatch.setattr(cfg_mod, "DEFAULT_SPEC_CANDIDATES", [
        openapi_dir / "spec.json",
        openapi_dir / "spec.yaml",
    ])
    monkeypatch.setattr(cfg_mod, "DEFAULT_CONFIG", openapi_dir / "config.yaml")

    from apiup.config import load_config
    config = load_config()
    assert config.spec.endswith("spec.json")


def test_default_spec_falls_back_to_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """spec.yaml is used when spec.json does not exist."""
    import apiup.config as cfg_mod

    openapi_dir = tmp_path / ".openapi"
    openapi_dir.mkdir()
    (openapi_dir / "spec.yaml").write_text("openapi: 3.0.3\ninfo:\n  title: T\n  version: '1'\npaths: {}")

    monkeypatch.setattr(cfg_mod, "DEFAULT_CONFIG_DIR", openapi_dir)
    monkeypatch.setattr(cfg_mod, "DEFAULT_SPEC_CANDIDATES", [
        openapi_dir / "spec.json",
        openapi_dir / "spec.yaml",
    ])
    monkeypatch.setattr(cfg_mod, "DEFAULT_CONFIG", openapi_dir / "config.yaml")

    from apiup.config import load_config
    config = load_config()
    assert config.spec.endswith("spec.yaml")
