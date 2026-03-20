"""
apiup — Start a local mock REST API server from an OpenAPI 3.x spec.

Convention: reads ~/.openapi/spec.yaml by default.

    apiup                        # reads ~/.openapi/spec.yaml, starts on :8080
    apiup --spec ./my-api.yaml
    apiup --port 9000
    apiup --list
"""

__version__ = "0.4.0"
__author__ = "roebi"
