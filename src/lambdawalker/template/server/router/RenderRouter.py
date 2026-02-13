import os
import json
from typing import Tuple, TYPE_CHECKING
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse

if TYPE_CHECKING:
    from lambdawalker.template.server.TemplateServer import TemplateServer

class RenderRouter:
    def __init__(self, server: 'TemplateServer'):
        self.server = server
        self.router = APIRouter(prefix="/render")
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("/{template_type}/{variant}/{record_id:int}")
        def render_card_by_record(
                template_type: str,
                variant: str,
                record_id: int,
                request: Request,
                primary_color: Tuple[float, float, float, float] = (0, 0, 0, 1)
        ):
            path = os.path.join(template_type, variant, "index.html.j2")
            if not self.server.site_path.joinpath(path).exists():
                raise HTTPException(status_code=404, detail="Template not found")

            env_path = str(self.server.site_path.joinpath(template_type, variant, "meta", "common.json"))
            common = {}

            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    common = json.load(f)

            return self.server.renderer.render_template(
                path,
                request,
                primary_color,
                data={
                    "data": {
                        "id": record_id
                    },
                    "common": common
                }
            )

        @self.router.get("/{template_type}/{variant}/")
        def render_card_by_random_record(
                template_type: str,
                variant: str,
                request: Request,
                primary_color: Tuple[float, float, float, float] = (0, 0, 0, 1)
        ):
            path = os.path.join(template_type, variant, "index.html.j2")
            if not self.server.site_path.joinpath(path).exists():
                raise HTTPException(status_code=404, detail="Template not found")

            env_path = str(self.server.site_path.joinpath(template_type, variant, "meta", "common.json"))
            common = {}

            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    common = json.load(f)

            return self.server.renderer.render_template(
                path,
                request,
                primary_color,
                data={
                    "data": {
                        "id": "random"
                    },
                    "common": common
                }
            )

        @self.router.get("/{template_type}/{variant}")
        def render_card_random_record_redirect(
                template_type: str,
                variant: str,
        ):
            return RedirectResponse(
                url=f"/render/{template_type}/{variant}/",
                status_code=307,
            )
