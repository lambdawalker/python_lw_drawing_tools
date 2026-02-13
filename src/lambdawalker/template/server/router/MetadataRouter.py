from typing import TYPE_CHECKING

from fastapi import APIRouter

if TYPE_CHECKING:
    from lambdawalker.template.server.TemplateServer import TemplateServer


class MetadataRouter:
    def __init__(self, server: 'TemplateServer'):
        self.server = server
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/summary")
        def get_summary():
            return self.server.handel_path_info.get_template_summary()

        @self.router.api_route("/{path:path}", methods=["INFO"])
        def handle_info(path: str):
            return self.server.handel_path_info(path)

