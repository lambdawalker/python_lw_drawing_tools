from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import FileResponse

if TYPE_CHECKING:
    from lambdawalker.template.server.TemplateServer import TemplateServer


class AssetRouter:
    def __init__(self, server: 'TemplateServer'):
        self.server = server
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/render/{path:path}")
        def serve_relative_to_site(path: str, request: Request):
            if path.endswith(".j2"):
                return render_jinja_any(path, request)

            full_path = self.server.site_path.joinpath(path)
            if not full_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            return FileResponse(path=str(full_path))

        @self.router.get("/{path:path}")
        def render_jinja_any(path: str, request: Request):
            if path == "":
                path = "index.html.j2"

            if not path.endswith(".j2"):
                raise HTTPException(status_code=404)

            template_path = self.server.site_path / path
            if not template_path.exists():
                raise HTTPException(status_code=404)

            return self.server.renderer.render_template(path, request)
