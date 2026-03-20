"""
Build a Litestar ASGI app from a parsed OpenAPI spec (mock mode).
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from apiup.mock import extract_mock_response
from apiup.spec import Route

try:
    from litestar import Litestar
    from litestar.handlers import HTTPRouteHandler
    from litestar.response import Response as LitestarResponse
except ImportError:  # pragma: no cover
    Litestar = None  # type: ignore[assignment,misc]
    HTTPRouteHandler = None  # type: ignore[assignment,misc]
    LitestarResponse = None  # type: ignore[assignment]

# OpenAPI {param} → Litestar {param:str}
_PARAM_RE = re.compile(r"\{(\w+)\}")

# Status codes that must not have a response body
_NO_BODY_CODES = frozenset({204, 304})


def _openapi_path_to_litestar(path: str) -> str:
    """Convert /skills/{skillId} → /skills/{skillId:str}."""
    return _PARAM_RE.sub(r"{\1:str}", path)


def _make_handler(body: Any, status_code: int) -> Any:
    """Return a handler closed over body+status — no mutable defaults."""
    if status_code in _NO_BODY_CODES:
        # No-body response — return None, Litestar sends empty 204/304
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


def build_mock_app(routes: list[Route], spec: dict[str, Any]) -> Any:
    """Return a Litestar ASGI app with one handler per spec route."""
    if Litestar is None:
        print(
            "ERROR: litestar not installed.\nRun: pip install 'litestar[standard]'",
            file=sys.stderr,
        )
        sys.exit(2)

    handlers = []

    for route in routes:
        status_code, body = extract_mock_response(route.responses, spec)
        litestar_path = _openapi_path_to_litestar(route.path)

        handler = HTTPRouteHandler(
            path=litestar_path,
            http_method=route.method,
            status_code=status_code,
        )(_make_handler(body, status_code))

        handlers.append(handler)

    return Litestar(route_handlers=handlers, debug=False)


def serve(app: Any, host: str, port: int) -> None:
    """Start uvicorn with the given app."""
    try:
        import uvicorn
    except ImportError:
        print(
            "ERROR: uvicorn not installed.\nRun: pip install uvicorn",
            file=sys.stderr,
        )
        sys.exit(2)

    uvicorn.run(app, host=host, port=port, log_level="warning")
