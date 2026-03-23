import traceback
import urllib.parse
from typing import Tuple

import requests

from lambdawalker.draw.color.generate_color import generate_hsluv_black_text_contrasting_color
from lambdawalker.template.SyncPlaywrightRenderer import SyncPlaywrightRenderer
from lambdawalker.template.render.CardImageProcessor import CardImageProcessor
from lambdawalker.template.render.CardMetadataHandler import CardMetadataHandler


def fetch_available_templates(base_url: str) -> Tuple[str, ...]:
    available_templates_resp = requests.request("INFO", f"{base_url}/id_cards/", timeout=10)
    available_templates_resp.raise_for_status()
    available_templates = available_templates_resp.json()

    return tuple((
        t["name"] for t in available_templates if not t['name'].startswith("_")
    ))


class CardRenderer:
    def __init__(self, base_url: str, outdir: str = "./output/", headless: bool = True, log=lambda m: None, report_progress=lambda p: None):
        self.base_url = base_url
        self.outdir = outdir
        self.headless = headless
        self.renderer = SyncPlaywrightRenderer(log=log, report_progress=report_progress)
        self._available_templates = None
        self.image_processor = CardImageProcessor(outdir)
        self.metadata_handler = CardMetadataHandler(base_url, outdir)
        self.counter = 0
        self.log = log
        self.report_progress = report_progress

    def start(self):
        self.renderer.start(headless=self.headless)

    def close(self):
        self.renderer.close()

    def render_single_card(self, record_id: int, template_name: str):
        if self.metadata_handler.record_exists(record_id, template_name):
            reporting_message = f"Skipping {template_name} {record_id} because it already exists"
            self.log(reporting_message)
            self.report_progress(1)
            return

        primary_color = generate_hsluv_black_text_contrasting_color()

        tuple_str = ",".join(map(str, primary_color.to_hsl_tuple()))
        escaped_tuple = urllib.parse.quote(tuple_str)

        data_id = self.counter
        self.counter += 1

        url = (
            f"{self.base_url}/render/id_cards/{template_name}/{data_id}"
            f"?primary_color={escaped_tuple}"
        )
        self.log(f"Rendering {template_name} {record_id} from {url}")
        self.report_progress(.25)

        page = self.renderer.page
        page.goto(url)
        self.report_progress(.5)

        card = page.wait_for_selector("#view-port")
        image_bytes = card.screenshot(omit_background=True)
        self.report_progress(.6)

        first_layer_image = self.image_processor.process_and_save_image(
            image_bytes, record_id, template_name, primary_color
        )
        self.log("Processed image")

        meta = self.metadata_handler.fetch_template_meta(template_name)
        self.log("Fetched meta")
        self.report_progress(.7)

        w, h = first_layer_image.size
        elements = [{
            "class": meta["class"],
            "boundingBox": [0, 0, w, h],
            "subtype": template_name,
            "photo_id": data_id
        }] + self.capture_elements()

        self.log("Captured elements")
        self.report_progress(.8)

        self.metadata_handler.save_object_detection_log(record_id, template_name, elements)
        self.report_progress(1)
        self.log("Saved object detection log")

    def capture_elements(self):
        page = self.renderer.page
        selector = "[data-class]"

        # Ensure at least one exists before continuing
        page.wait_for_selector(selector)

        # Grab all matching elements
        handles = page.query_selector_all(selector)

        results = []
        for el in handles:
            # attribute value (string or None)
            val = el.get_attribute("data-class")

            # bounding box (dict or None; can be None if not visible / not in layout)
            box = el.bounding_box()
            if not box:
                continue  # skip elements without a box (display:none, etc.)

            results.append({
                "class": val if val is not None else "",
                "bbox": [box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"]],
            })

        return results
