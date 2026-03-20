"""
apiup CLI entrypoint.
"""

from __future__ import annotations

import argparse
import sys

from apiup import __version__
from apiup.config import load_config
from apiup.spec import extract_routes, load_spec, spec_info


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="apiup",
        description=(
            "Start a local mock REST API server from an OpenAPI 3.x spec.\n"
            "Convention: reads ~/.openapi/spec.json by default."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  apiup                          # mock server from ~/.openapi/spec.json\n"
            "  apiup --spec ./orders.yaml     # custom spec\n"
            "  apiup --port 9000              # custom port\n"
            "  apiup --list                   # list routes, no server\n"
            "  apiup --validate               # validate spec and exit\n"
        ),
    )
    p.add_argument("--spec", default=None, help="Path to OpenAPI spec (.json or .yaml)")
    p.add_argument("--port", type=int, default=None, help="Port to listen on (default: 8080)")
    p.add_argument("--host", default=None, help="Host to bind (default: 127.0.0.1)")
    p.add_argument("--mode", choices=["mock"], default=None, help="Server mode (default: mock)")
    p.add_argument("--list", action="store_true", help="List routes and exit (no server)")
    p.add_argument(
        "--validate", action="store_true", help="Validate spec and exit (requires apiup[validate])"
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    cfg = load_config(
        spec=args.spec,
        port=args.port,
        host=args.host,
        mode=args.mode,
    )

    spec = load_spec(cfg.spec)
    routes = extract_routes(spec)
    title, version = spec_info(spec)

    if args.validate:
        from apiup.validate import validate_spec

        ok = validate_spec(spec, cfg.spec)
        sys.exit(0 if ok else 1)

    if args.list:
        print(f"\nRoutes in: {cfg.spec}\n")
        for r in routes:
            note = f"  # {r.summary}" if r.summary else ""
            print(f"  {r.method:<8} {r.path}{note}")
        print(f"\n{len(routes)} route(s) found.\n")
        return

    # ── Banner ──────────────────────────────────────────────────────────────
    print(f"\n⚡ apiup {__version__} — {title} v{version}")
    print(f"   Spec  : {cfg.spec}")
    print(f"   Mode  : {cfg.mode}")
    print(f"   Listen: http://{cfg.host}:{cfg.port}")
    print(f"   Docs  : http://{cfg.host}:{cfg.port}/docs")
    print(f"   Spec  : http://{cfg.host}:{cfg.port}/spec.json")
    print(f"   Routes: {len(routes)}")
    print()
    for r in routes:
        print(f"   {r.method:<8} {r.path}")
    print()

    # ── Build + serve ────────────────────────────────────────────────────────
    from apiup.server import build_mock_app, serve

    app = build_mock_app(routes, spec, cfg.spec)
    serve(app, host=cfg.host, port=cfg.port)


if __name__ == "__main__":
    main()
