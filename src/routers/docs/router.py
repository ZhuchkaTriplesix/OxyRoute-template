from __future__ import annotations

from oxyroute import APIRouter, Depends, Response

from src.routers.docs.dependencies import basic_auth_guard

docs_router = APIRouter()

SCALAR_HTML = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>OxyRoute API Docs</title>
  </head>
  <body>
    <script
      id="api-reference"
      data-url="/openapi.json"
      data-theme="default"
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>
"""


@docs_router.get("/docs", dependencies=[("user", Depends(basic_auth_guard))])
def docs_page() -> Response:
    return Response(
        body=SCALAR_HTML,
        headers={"content-type": "text/html; charset=utf-8"},
    )
