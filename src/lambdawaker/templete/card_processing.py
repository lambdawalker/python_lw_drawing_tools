import json
import os
from io import BytesIO
from typing import List, Dict, Any

import requests
import yaml
from PIL import Image

from lambdawaker.draw import card_background as card_background_module
from lambdawaker.file.path.ensure_directory import ensure_directory_for_file
from lambdawaker.reflection.query import select_random_function_from_module_and_submodules


class CardImageProcessor:
    def __init__(self, outdir: str):
        self.outdir = outdir

    def process_and_save_image(self, image_bytes: bytes, record_id: int, template_name: str, primary_color) -> Image.Image:
        background_paint_function = select_random_function_from_module_and_submodules(
            card_background_module,
            "generate_card_background_.*",
        )

        first_layer_image = Image.open(BytesIO(image_bytes))

        _, card_background_image = background_paint_function(
            first_layer_image.size,
            primary_color,
        )

        canvas = Image.new("RGBA", first_layer_image.size)
        for image in [card_background_image, first_layer_image]:
            canvas.paste(image, (0, 0), image)

        image_output_path = os.path.join(self.outdir, "img", f"{record_id}_{template_name}.png")
        ensure_directory_for_file(image_output_path)
        canvas.save(image_output_path)
        return first_layer_image


class CardMetadataHandler:
    def __init__(self, base_url: str, outdir: str):
        self.base_url = base_url
        self.outdir = outdir

    def fetch_template_meta(self, template_name: str) -> Dict[str, Any]:
        raw_meta = requests.get(f"{self.base_url}/render/id_cards/{template_name}/meta.yaml")
        raw_meta.raise_for_status()
        return yaml.safe_load(raw_meta.text)

    def save_object_detection_log(self, record_id: int, template_name: str, elements: List[Dict[str, Any]]):
        obj_detection_log_path = os.path.join(self.outdir, "obj", f"{record_id}_{template_name}.json")
        ensure_directory_for_file(obj_detection_log_path)
        with open(obj_detection_log_path, "w") as f:
            f.write(json.dumps(elements))
