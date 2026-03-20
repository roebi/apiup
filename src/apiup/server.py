"""
Build a Litestar ASGI app from a parsed OpenAPI spec (mock mode).
"""

from __future__ import annotations

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
        _method = route.method
        _path = route.path
        _body = body
        _status = status_code

        # Return type is Any — avoids NameError when Litestar inspects
        # the handler signature in a scope where Response is not global.
        async def _handler(b: Any = _body, s: int = _status) -> Any:  # noqa: B023
            return LitestarResponse(content=b, status_code=s, media_type="application/json")

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
