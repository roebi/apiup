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

With [uv](https://docs.astral.sh/uv/):

```bash
uv tool install apiup
```

With validation support:

```bash
pip install 'apiup[validate]'
```

## Convention: `~/.openapi/`

`apiup` follows an XDG-style user convention — place your default spec at:

```
~/.openapi/spec.json      ← preferred
~/.openapi/spec.yaml      ← fallback
```

Optional config:

```yaml
# ~/.openapi/config.yaml
port: 8080
host: 127.0.0.1
mode: mock
spec: ~/.openapi/spec.json
```

## Usage

```bash
apiup                          # reads ~/.openapi/spec.json, starts on :8080
apiup --spec ./my-api.yaml     # custom spec path
apiup --port 9000              # custom port
apiup --host 0.0.0.0           # bind all interfaces
apiup --list                   # list routes without starting server
apiup --validate               # validate spec against OpenAPI 3.x schema
apiup --version
apiup --help
```

## Example session

```
$ apiup --validate
   Validating: /home/roebi/.openapi/spec.json
   OpenAPI   : 3.0.3
   Title     : My API v1.0.0
   ✓ spec valid  (7 route(s))

$ apiup --list
Routes in: /home/roebi/.openapi/spec.json

  GET      /skills        # List all skills
  POST     /skills        # Create a new skill
  GET      /skills/{id}   # Get skill details
  DELETE   /skills/{id}   # Delete a skill

4 route(s) found.

$ apiup
⚡ apiup 0.6.0 — My API v1.0.0
   Spec  : /home/roebi/.openapi/spec.json
   Mode  : mock
   Listen: http://127.0.0.1:8080
   Docs  : http://127.0.0.1:8080/docs
   Spec  : http://127.0.0.1:8080/spec.json
   Routes: 4

$ curl http://localhost:8080/skills
[{"id": "create-agent-skill-en", "name": "Create Agent Skill", "version": "1.0.0"}]
```

## Built-in endpoints

Every `apiup` instance exposes two additional routes:

| Endpoint | Description |
|---|---|
| `GET /docs` | Swagger UI (no extra dependencies) |
| `GET /spec.json` | Raw OpenAPI spec served directly |

## Mock behaviour

In mock mode `apiup`:

- Registers one route handler per `[METHOD] /path` in the spec
- Returns the first `example` value found in the spec responses
- Falls back to `{"_mock": true, "note": "no example in spec"}` if none present
- Returns `204 No Content` with no body for routes that declare it
- Resolves local `$ref` pointers in spec components

Add `example:` fields to your spec responses to get real data back:

```yaml
/skills:
  get:
    responses:
      "200":
        content:
          application/json:
            example:
              - id: create-agent-skill-en
                name: Create Agent Skill
                version: "1.0.0"
```

## Server modes

| Mode | Status | Description |
|---|---|---|
| `mock` | ✓ available | returns spec examples |
| `proxy` | planned | forwards requests to a real backend |
| `record` | planned | proxy + saves real responses as spec examples |

## Validation

```bash
pip install 'apiup[validate]'
apiup --validate
apiup --validate --spec ./my-api.yaml

# use in CI — exits 1 if spec is invalid
apiup --validate || exit 1
```

Requires `openapi-spec-validator`. If not installed, `--validate` warns but does not block startup.

## Python API

```python
from apiup.spec import load_spec, extract_routes
from apiup.mock import extract_mock_response
from apiup.server import build_mock_app, serve
from apiup.config import load_config

cfg    = load_config(spec="./my-api.yaml", port=9000)
spec   = load_spec(cfg.spec)
routes = extract_routes(spec)
app    = build_mock_app(routes, spec, cfg.spec)
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
