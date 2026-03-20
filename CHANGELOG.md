# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-19

### Added
- `apiup` CLI: `--spec`, `--port`, `--host`, `--mode`, `--list`, `--version`
- `~/.openapi/spec.yaml` default spec convention (XDG-style)
- `~/.openapi/config.yaml` optional config file
- Mock mode: returns `example` fields from spec as HTTP responses
- Local `$ref` resolution for spec components
- `204 No Content` handling for DELETE routes
- Stub fallback `{"_mock": true}` for routes with no examples
- Python API: `load_spec`, `extract_routes`, `extract_mock_response`, `build_mock_app`, `serve`
- `python -m apiup` support
- Litestar + uvicorn backend
- GitHub Actions CI (Python 3.11, 3.12) with ruff lint + mypy (non-blocking)
- PyPI publish via OIDC Trusted Publishing (no tokens)
- Devcontainer for maintainers
