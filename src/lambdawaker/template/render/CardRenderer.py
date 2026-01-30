from typing import Tuple

import requests

from lambdawaker.draw.color.generate_color import generate_hsluv_black_text_contrasting_color
from lambdawaker.template.AsyncPlaywrightRenderer import AsyncPlaywrightRenderer
from lambdawaker.template.render.CardImageProcessor import CardImageProcessor
from lambdawaker.template.render.CardMetadataHandler import CardMetadataHandler


def fetch_available_templates(base_url: str) -> Tuple[str, ...]:
    available_templates_resp = requests.request("INFO", f"{base_url}/id_cards/", timeout=10)
    available_templates_resp.raise_for_status()
    available_templates = available_templates_resp.json()

    return tuple((
        t["name"] for t in available_templates if not t['name'].startswith("_")
    ))


class CardRenderer:
    def __init__(self, base_url: str, outdir: str = "./output/", headless: bool = True):
        self.base_url = base_url
        self.outdir = outdir
        self.headless = headless
        self.renderer = AsyncPlaywrightRenderer()
        self._available_templates = None
        self.image_processor = CardImageProcessor(outdir)
        self.metadata_handler = CardMetadataHandler(base_url, outdir)

    async def start(self):
        await self.renderer.start(headless=self.headless)

    async def close(self):
        await self.renderer.close()

    async def get_available_templates(self) -> Tuple[str, ...]:
        if self._available_templates is None:
            self._available_templates = fetch_available_templates(self.base_url)
        return self._available_templates

    async def render_record(self, record_id: int):
        templates = await self.get_available_templates()
        for template_name in templates:
            await self.render_single_card(record_id, template_name)

    async def render_single_card(self, record_id: int, template_name: str):
        primary_color = generate_hsluv_black_text_contrasting_color()

        url = (
            f"{self.base_url}/render/id_cards/{template_name}/{record_id}"
            f"?primary_color={primary_color.to_hsl_tuple()}"
        )

        page = self.renderer.page
        await page.goto(url)

        card = await page.wait_for_selector("#view-port")
        image_bytes = await card.screenshot(omit_background=True)

        first_layer_image = self.image_processor.process_and_save_image(
            image_bytes, record_id, template_name, primary_color
        )

        meta = self.metadata_handler.fetch_template_meta(template_name)

        w, h = first_layer_image.size
        elements = [{
            "class": meta["class"],
            "box": [0, 0, w, h]
        }]  # + await self.capture_elements()

        self.metadata_handler.save_object_detection_log(record_id, template_name, elements)

    async def capture_elements(self):
        page = self.renderer.page
        selector = "[data-class]"

        # Ensure at least one exists before continuing
        await page.wait_for_selector(selector)

        # Grab all matching elements
        handles = await page.query_selector_all(selector)

        results = []
        for el in handles:
            # attribute value (string or None)
            val = await el.get_attribute("data-class")

            # bounding box (dict or None; can be None if not visible / not in layout)
            box = await el.bounding_box()
            if not box:
                continue  # skip elements without a box (display:none, etc.)

            results.append({
                "class": val if val is not None else "",
                "bbox": [box["x"], box["y"], box["width"], box["height"]],
            })

        return results
