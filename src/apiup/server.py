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


def _make_handler(body: Any, status_code: int) -> Any:
    """Return a handler function closed over body+status.

    Defined at module level (not inside a loop) so Litestar's signature
    inspection never sees a mutable default value — the values are captured
    in the closure, not as default arguments.
    """
    import json

    # Serialise once; send bytes to avoid Litestar re-encoding a dict default.
    if body is None:
        raw: bytes | None = None
    else:
        raw = json.dumps(body).encode()

    async def _handler() -> Any:
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

        handler_fn = _make_handler(body, status_code)

        handler = HTTPRouteHandler(
            path=route.path,
            http_method=route.method,
            status_code=status_code,
        )(handler_fn)

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
