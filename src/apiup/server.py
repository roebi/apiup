"""
Build a Litestar ASGI app from a parsed OpenAPI spec (mock mode).
"""

from __future__ import annotations

import sys
from typing import Any

from apiup.mock import extract_mock_response
from apiup.spec import Route


def build_mock_app(routes: list[Route], spec: dict[str, Any]) -> Any:
    """Return a Litestar ASGI app with one handler per spec route."""
    try:
        from litestar import Litestar
        from litestar.handlers import HTTPRouteHandler
        from litestar.response import Response
    except ImportError:
        print(
            "ERROR: litestar not installed.\nRun: pip install 'litestar[standard]'",
            file=sys.stderr,
        )
        sys.exit(2)

    handlers = []

    for route in routes:
        status_code, body = extract_mock_response(route.responses, spec)
        _method = route.method
        _path = route.path
        _body = body
        _status = status_code

        # Litestar uses the same {param} syntax as OpenAPI — no conversion needed.
        async def _handler(b: Any = _body, s: int = _status) -> Response:  # noqa: B023
            return Response(content=b, status_code=s, media_type="application/json")

        handler = HTTPRouteHandler(
            path=_path,
            http_method=_method,
            status_code=_status,
        )(_handler)

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
