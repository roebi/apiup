"""
Mock response extraction from OpenAPI spec examples.

Priority order per route:
  1. responses.200.content.application/json.example
  2. responses.201.content.application/json.example
  3. responses.202.content.application/json.example
  4. responses.200.content.application/json.examples.<first>.value
  5. responses.200.content.application/json.schema.example
  6. responses.default.*  (same chain)
  7. Stub: {"_mock": true, "note": "no example in spec"}
"""

from __future__ import annotations

from typing import Any


def resolve_ref(ref: str, spec: dict[str, Any]) -> dict[str, Any]:
    """Resolve a local JSON $ref pointer (e.g. #/components/examples/Foo)."""
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for part in parts:
        if not isinstance(node, dict):
            return {}
        node = node.get(part, {})
    return node if isinstance(node, dict) else {}


def _extract_from_media(media: dict[str, Any], spec: dict[str, Any]) -> Any | None:
    """Try to pull an example value from a media type object."""
    if "example" in media:
        return media["example"]
    if "examples" in media:
        first = next(iter(media["examples"].values()), {})
        if "$ref" in first:
            first = resolve_ref(first["$ref"], spec)
        return first.get("value")
    schema = media.get("schema", {})
    if "$ref" in schema:
        schema = resolve_ref(schema["$ref"], spec)
    if "example" in schema:
        return schema["example"]
    return None


def extract_mock_response(
    responses: dict[str, Any],
    spec: dict[str, Any],
) -> tuple[int, Any]:
    """Return (http_status_code, response_body) for mock mode."""
    for status_str in ("200", "201", "202", "204", "default"):
        resp = responses.get(status_str)
        if resp is None:
            continue

        if "$ref" in resp:
            resp = resolve_ref(resp["$ref"], spec)

        # 204 No Content — never has a body
        if status_str == "204":
            return 204, None

        content = resp.get("content", {})
        media = content.get("application/json", content.get("*/*", {}))

        if media:
            value = _extract_from_media(media, spec)
            if value is not None:
                code = int(status_str) if status_str.isdigit() else 200
                return code, value

        # Response exists but has no content — return empty stub
        code = int(status_str) if status_str.isdigit() else 200
        return code, {"_mock": True, "status": code, "note": "no example in spec"}

    return 200, {"_mock": True, "note": "no response defined in spec"}
