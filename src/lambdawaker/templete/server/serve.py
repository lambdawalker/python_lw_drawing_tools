import mimetypes
import os
from pathlib import Path
from typing import Tuple

from fastapi import FastAPI
from fastapi import HTTPException
from jinja2 import FileSystemLoader, select_autoescape
from starlette.requests import Request
from starlette.responses import Response, FileResponse
from starlette.staticfiles import StaticFiles

from lambdawaker.dataset.DiskDataset import DiskDataset
from lambdawaker.dataset.hadlers.DatasetSourceHandler import DataSetsHandler
from lambdawaker.dataset.hadlers.process_data_payload import process_data_payload
from lambdawaker.draw.color.HSLuvColor import to_hsluv_color
from lambdawaker.draw.color.generate_color import generate_hsluv_black_text_contrasting_color
from lambdawaker.templete.fields import field_generators
from lambdawaker.templete.server.FileMetadataHandler import FileMetadataHandler
from lambdawaker.templete.server.RelativeLoader import RelativeEnvironment

app = FastAPI()

SITE_ROOT = Path("./site").resolve()

env = RelativeEnvironment(
    loader=FileSystemLoader(str(SITE_ROOT)),
    autoescape=select_autoescape(["html", "xml", "svg"]),
)

person_ds = DiskDataset(dataset_id="lambdaWalker/ds.photo_id")
person_ds.load("@DS/lw_person_V0.0.0")

dataset_handler = DataSetsHandler([
    person_ds
])


def render_template(path: str, request: Request, primary_color=None, data=None) -> Response:
    data = data if data is not None else {}
    path = path.replace("\\", "/")

    primary_color = to_hsluv_color(primary_color) if primary_color is not None else generate_hsluv_black_text_contrasting_color()
    text_color_hex = to_hsluv_color((0, 0, 0, 1))

    default_env = {
        "theme": {
            "primary_color": primary_color,
            "text_color": text_color_hex
        }
    }

    output_name = path[:-3]  # remove ".j2"
    media_type, _ = mimetypes.guess_type(output_name)
    media_type = media_type or "text/plain"

    template = env.get_template(path)

    rendered = template.render(
        request=request,
        env=default_env,
        gen=field_generators,
        ds=dataset_handler,
        **data
    )

    return Response(
        content=rendered,
        media_type=media_type
    )


@app.get("/render/{template_type}/{variant}/{record_id:int}")
def render_card_by_record(template_type: str, variant: str, record_id: int, request: Request, primary_color: Tuple[float, float, float, float] = [0, 0, 0, 1]):
    print("render_card_by_record")
    path = os.path.join("/", template_type, variant, "index.html.j2")

    env_path = str(SITE_ROOT.joinpath(template_type, variant, "meta", "common.json"))
    common = {}

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            import json
            common = json.load(f)

    return render_template(
        path,
        request,
        primary_color,
        data={
            "data": {
                "record": person_ds[record_id],
                "id": record_id
            },
            "common": common
        }
    )


@app.get("/render/{path:path}")
def serve_relative_to_site(path: str, request: Request):
    if path.endswith(".j2"):
        return render_jinja_any(path, request)

    result = str(SITE_ROOT.joinpath(path))
    return FileResponse(
        path=result
    )


@app.get("/ds/{path:path}")
def server_dataset_resource(path: str):
    print("server_dataset_resource")
    data = dataset_handler[path]
    content_type, data = process_data_payload(data)
    return Response(
        content=data,
        media_type=content_type
    )


@app.get("/{path:path}")
def render_jinja_any(path: str, request: Request):
    print("render_jinja_any")
    if path == "":
        path = "index.html.j2"

    print(path)

    if not path.endswith(".j2"):
        raise HTTPException(status_code=404)

    template_path = SITE_ROOT / path
    if not template_path.exists():
        raise HTTPException(status_code=404)

    return render_template(path, request)


handel_path_info = FileMetadataHandler(SITE_ROOT)


@app.api_route("/{path:path}", methods=["INFO"])
def handle_info(path: str):
    return handel_path_info(path)


SITE_ROOT = Path("./site").resolve()
app.mount("/", StaticFiles(directory="./site"), name="site")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("serve:app", host="0.0.0.0", port=8001, workers=32)
