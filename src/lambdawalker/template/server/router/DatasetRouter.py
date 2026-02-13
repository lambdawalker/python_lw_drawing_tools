from typing import TYPE_CHECKING
from fastapi import APIRouter, HTTPException, Response
from lambdawalker.dataset.hadlers.process_data_payload import process_data_payload

if TYPE_CHECKING:
    from lambdawalker.template.server.TemplateServer import TemplateServer

class DatasetRouter:
    def __init__(self, server: 'TemplateServer'):
        self.server = server
        self.router = APIRouter(prefix="/ds")
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/{path:path}")
        def server_dataset_resource(path: str):
            try:
                data = self.server.dataset_handler[path]
            except (KeyError, IndexError, ValueError):
                raise HTTPException(status_code=404, detail="Dataset resource not found")

            content_type, data = process_data_payload(data)
            if content_type is None:
                raise HTTPException(status_code=404, detail="Dataset resource processing failed")
            return Response(content=data, media_type=content_type)
