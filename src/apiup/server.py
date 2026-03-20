"""
Build a Litestar ASGI app from a parsed OpenAPI spec (mock mode).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from apiup.mock import extract_mock_response
from apiup.spec import Route

try:
    from litestar import Litestar, get
    from litestar.handlers import HTTPRouteHandler
    from litestar.response import Response as LitestarResponse
except ImportError:  # pragma: no cover
    Litestar = None  # type: ignore[assignment,misc]
    HTTPRouteHandler = None  # type: ignore[assignment,misc]
    LitestarResponse = None  # type: ignore[assignment]
    get = None  # type: ignore[assignment]

_PARAM_RE = re.compile(r"\{(\w+)\}")
_NO_BODY_CODES = frozenset({204, 304})

_SWAGGER_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>apiup — Swagger UI</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>
SwaggerUIBundle({
  url: "/spec.json",
  dom_id: "#swagger-ui",
  presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
  layout: "BaseLayout",
  deepLinking: true
})
</script>
</body>
</html>"""


def _openapi_path_to_litestar(path: str) -> str:
    return _PARAM_RE.sub(r"{\1:str}", path)


def _make_handler(body: Any, status_code: int) -> Any:
    if status_code in _NO_BODY_CODES:

        async def _handler() -> None:
            return None
    else:
        raw: bytes = b"null" if body is None else json.dumps(body).encode()

        async def _handler() -> Any:  # type: ignore[misc]
            return LitestarResponse(
                content=raw,
                status_code=status_code,
                media_type="application/json",
            )

    return _handler


def build_mock_app(routes: list[Route], spec: dict[str, Any], spec_path: str) -> Any:
    """Return a Litestar ASGI app with mock handlers + swagger UI."""
    if Litestar is None:
        print(
            "ERROR: litestar not installed.\nRun: pip install 'litestar[standard]'",
            file=sys.stderr,
        )
        sys.exit(2)

    # ── built-in routes ────────────────────────────────────────────────────
    spec_bytes: bytes = Path(spec_path).read_bytes()

    @get("/spec.json", media_type="application/json")
    async def serve_spec() -> LitestarResponse:  # type: ignore[return]
        return LitestarResponse(
            content=spec_bytes,
            status_code=200,
            media_type="application/json",
        )

    @get("/docs", media_type="text/html")
    async def serve_docs() -> LitestarResponse:  # type: ignore[return]
        return LitestarResponse(
            content=_SWAGGER_HTML.encode(),
            status_code=200,
            media_type="text/html",
        )

    # ── mock route handlers ────────────────────────────────────────────────
    handlers: list[Any] = [serve_spec, serve_docs]

    for route in routes:
        status_code, body = extract_mock_response(route.responses, spec)
        litestar_path = _openapi_path_to_litestar(route.path)

        handler = HTTPRouteHandler(
            path=litestar_path,
            http_method=route.method,
            status_code=status_code,
        )(_make_handler(body, status_code))

        handlers.append(handler)

    return Litestar(route_handlers=handlers, openapi_config=None, debug=False)


def serve(app: Any, host: str, port: int) -> None:
    try:
        import uvicorn
    except ImportError:
        print(
            "ERROR: uvicorn not installed.\nRun: pip install uvicorn",
            file=sys.stderr,
        )
        sys.exit(2)

    uvicorn.run(app, host=host, port=port, log_level="warning")
