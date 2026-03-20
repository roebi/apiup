# apiup

> ⚡ Start a local mock REST API server from an OpenAPI 3.x spec — one command.

[![CI](https://github.com/roebi/apiup/actions/workflows/ci.yml/badge.svg)](https://github.com/roebi/apiup/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/apiup)](https://pypi.org/project/apiup/)
[![Python](https://img.shields.io/pypi/pyversions/apiup)](https://pypi.org/project/apiup/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Install

```bash
pip install apiup
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install apiup
```

## Convention: `~/.openapi/`

`apiup` follows an XDG-style user convention — place your default spec at:

```
~/.openapi/spec.yaml
```

Optional config:

```yaml
# ~/.openapi/config.yaml
port: 8080
host: 127.0.0.1
mode: mock
spec: ~/.openapi/spec.yaml
```

## Usage

```bash
apiup                          # reads ~/.openapi/spec.yaml, starts on :8080
apiup --spec ./my-api.yaml     # custom spec path
apiup --port 9000              # custom port
apiup --host 0.0.0.0           # bind all interfaces
apiup --list                   # list routes without starting server
apiup --version
apiup --help
```

### Example session

```
$ apiup --list

Routes in: /home/roebi/.openapi/spec.yaml

  GET      /                      # Health check
  GET      /items                 # List all items
  POST     /items                 # Create an item
  GET      /items/{id}            # Get item by ID
  DELETE   /items/{id}            # Delete item by ID

5 route(s) found.

$ apiup
⚡ apiup 0.1.0 — My API v1.0.0
   Spec  : /home/roebi/.openapi/spec.yaml
   Mode  : mock
   Listen: http://127.0.0.1:8080
   Docs  : http://127.0.0.1:8080/schema/swagger
   Routes: 5

$ curl http://localhost:8080/items
[{"id": 1, "name": "Widget", "price": 9.99}]
```

## Python API

```python
from apiup.spec import load_spec, extract_routes
from apiup.mock import extract_mock_response
from apiup.server import build_mock_app, serve
from apiup.config import load_config

cfg    = load_config(spec="./my-api.yaml", port=9000)
spec   = load_spec(cfg.spec)
routes = extract_routes(spec)
app    = build_mock_app(routes, spec)
serve(app, host=cfg.host, port=cfg.port)
```

## Development

```bash
uv sync --all-extras
uv run pytest
uv run ruff check .
uv run ruff format .
```

## License

CC BY-NC-SA 4.0 — see [LICENSE](LICENSE).

Part of the [roebi agent-skills](https://github.com/roebi/agent-skills) ecosystem.
