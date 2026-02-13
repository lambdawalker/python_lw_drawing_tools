import mimetypes
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException
from jinja2 import FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateNotFound
from starlette.requests import Request
from starlette.responses import Response

from lambdawalker.draw.color.HSLuvColor import to_hsluv_color
from lambdawalker.draw.color.generate_color import generate_hsluv_black_text_contrasting_color
from lambdawalker.template.fields import field_generators
from lambdawalker.template.server.render.RelativeLoader import RelativeEnvironment


class TemplateRenderer:
    def __init__(self, site_path: str, dataset_handler: Any):
        self.site_path = site_path
        self.dataset_handler = dataset_handler
        self.env = RelativeEnvironment(
            loader=FileSystemLoader(str(self.site_path)),
            autoescape=select_autoescape(["html", "xml", "svg"]),
        )

    def render_template(self, path: str, request: Request, primary_color: Optional[Tuple[float, float, float, float]] = None, data: Optional[Dict[str, Any]] = None) -> Response:
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

        try:
            template = self.env.get_template(path)
        except TemplateNotFound:
            raise HTTPException(status_code=404, detail="Template not found")

        try:
            rendered = template.render(
                request=request,
                env=default_env,
                gen=field_generators,
                ds=self.dataset_handler,
                **data
            )
        except (KeyError, IndexError, ValueError) as e:
            # Often data access in template might fail if record doesn't exist
            raise HTTPException(status_code=404, detail=f"Data or template error: {str(e)}")

        return Response(
            content=rendered,
            media_type=media_type
        )
