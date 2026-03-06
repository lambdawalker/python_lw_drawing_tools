from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from lambdawalker.dataset.DiskDataset import DiskDataset
from lambdawalker.dataset.hadlers.DatasetSourceHandler import DataSetsHandler
from lambdawalker.template.server.metadata.FileMetadataHandler import FileMetadataHandler
from lambdawalker.template.server.render.TemplateRenderer import TemplateRenderer
from lambdawalker.template.server.router.TemplateRouter import TemplateRouter


class TemplateServer:
    def __init__(self, site_path: str, datasets: list):
        self.site_path = Path(site_path).resolve()
        self.datasets = datasets

        self.app = FastAPI()
        self._setup_datasets()
        self.renderer = TemplateRenderer(str(self.site_path), self.dataset_handler)
        self.handel_path_info = FileMetadataHandler(self.site_path)
        self.router = TemplateRouter(self)
        self._setup_routes()
        self._setup_static()

    def _setup_datasets(self):
        dataset_paths = self.datasets
        datasets = [DiskDataset(path) for path in dataset_paths]

        self.dataset_handler = DataSetsHandler(datasets)

    def _setup_routes(self):
        self.app.include_router(self.router.router)

    def _setup_static(self):
        self.app.mount("/", StaticFiles(directory=str(self.site_path)), name="site")
