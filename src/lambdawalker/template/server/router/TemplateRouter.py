from typing import TYPE_CHECKING

from fastapi import APIRouter

from lambdawalker.template.server.router.AssetRouter import AssetRouter
from lambdawalker.template.server.router.DatasetRouter import DatasetRouter
from lambdawalker.template.server.router.MetadataRouter import MetadataRouter
from lambdawalker.template.server.router.RenderRouter import RenderRouter

if TYPE_CHECKING:
    from lambdawalker.template.server.TemplateServer import TemplateServer


class TemplateRouter:
    def __init__(self, server: 'TemplateServer'):
        self.server = server
        self.router = APIRouter()
        self._setup_sub_routers()

    def _setup_sub_routers(self):
        # Specific routes should generally come before more generic ones
        self.render_router = RenderRouter(self.server)
        self.dataset_router = DatasetRouter(self.server)
        self.asset_router = AssetRouter(self.server)
        self.metadata_router = MetadataRouter(self.server)

        self.router.include_router(self.render_router.router)
        self.router.include_router(self.dataset_router.router)
        self.router.include_router(self.asset_router.router)
        self.router.include_router(self.metadata_router.router)
