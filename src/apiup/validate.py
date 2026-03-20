"""
OpenAPI spec validation using openapi-spec-validator (optional dependency).
"""

from __future__ import annotations

from typing import Any


def validate_spec(spec: dict[str, Any], spec_path: str) -> bool:
    """Validate spec against OpenAPI 3.x schema.

    Returns True if valid, False if invalid.
    Prints results to stdout.
    If openapi-spec-validator is not installed, warns and returns True (non-blocking).
    """
    try:
        from openapi_spec_validator import validate
        from openapi_spec_validator.readers import read_from_filename
    except ImportError:
        print(
            "  ⚠  openapi-spec-validator not installed — skipping deep validation.\n"
            "     Run: pip install 'apiup[validate]' to enable."
        )
        return True

    openapi_version = spec.get("openapi", spec.get("swagger", "?"))
    title, version = (
        spec.get("info", {}).get("title", "?"),
        spec.get("info", {}).get("version", "?"),
    )

    print(f"\n   Validating: {spec_path}")
    print(f"   OpenAPI   : {openapi_version}")
    print(f"   Title     : {title} v{version}")
    print()

    try:
        spec_dict, _ = read_from_filename(spec_path)
        validate(spec_dict)
        from apiup.spec import extract_routes

        routes = extract_routes(spec)
        print(f"   ✓ spec valid  ({len(routes)} route(s))\n")
        return True
    except Exception as exc:
        print("   ✗ spec invalid:\n")
        for line in str(exc).splitlines():
            print(f"      {line}")
        print()
        return False
