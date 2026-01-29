#!/usr/bin/env python3
import argparse
import asyncio
from io import BytesIO
from typing import Tuple

import requests
from PIL import Image

from lambdawaker.draw import card_background as card_background_module
from lambdawaker.draw.color.generate_color import generate_hsluv_black_text_contrasting_color
from lambdawaker.file.path.ensure_directory import ensure_directory
from lambdawaker.reflection.query import select_random_function_from_module_and_submodules
from lambdawaker.templete.AsyncPlaywrightRenderer import AsyncPlaywrightRenderer


def fetch_available_templates(base_url: str) -> Tuple[str, ...]:
    available_templates_resp = requests.request("INFO", f"{base_url}/id_cards/", timeout=10)
    available_templates_resp.raise_for_status()
    available_templates = available_templates_resp.json()

    return tuple((
        t["name"] for t in available_templates if not t['name'].startswith("_")
    ))


class CardRenderer:
    def __init__(self, base_url: str, outdir: str = "./output/img/", headless: bool = True):
        self.base_url = base_url
        self.outdir = outdir
        self.headless = headless
        self.renderer = AsyncPlaywrightRenderer()
        self._available_templates = None

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

        await self.renderer.page.goto(url)

        card = await self.renderer.page.wait_for_selector("#view-port")
        image_bytes = await card.screenshot(omit_background=True)

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

        ensure_directory(self.outdir)
        canvas.save(f"{self.outdir.rstrip('/')}/{record_id}_{template_name}.png")


async def render(
        ds_range: Tuple[int, int] = (0, 5),
        *,
        base_url: str,
        headless: bool = True,
        outdir: str = "./output/img/",
):
    print("STATUS: RUNNING")
    card_renderer = CardRenderer(base_url=base_url, outdir=outdir, headless=headless)
    await card_renderer.start()

    start, end = ds_range

    try:
        await card_renderer.get_available_templates()
    except Exception as e:
        print(f"MESSAGE: Failed to fetch templates: {e}")
        print("STATUS: FAILED")
        await card_renderer.close()
        return

    try:
        local_count = 0
        for record_id in range(start, end):
            print(f"MESSAGE: Processing record {record_id}")
            await card_renderer.render_record(record_id)

            local_count += 1
            print(f"PROGRESS: {local_count}")

        print("STATUS: SUCCESS")
    except Exception as e:
        print(f"MESSAGE: Error during rendering: {e}")
        print("STATUS: FAILED")
    finally:
        await card_renderer.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Render id card images for a range of record IDs."
    )

    p.add_argument("--start", default=0, type=int, help="Start record id (inclusive)")
    p.add_argument("--end", default=5, type=int, help="End record id (exclusive)")

    p.add_argument(
        "--base-url", required=True,
        help="Base server URL (default: %(default)s)",
    )
    p.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run browser headless (default: %(default)s). Use --no-headless to show UI.",
    )
    p.add_argument(
        "--outdir",
        default="./output/img/",
        help="Output directory (default: %(default)s)",
    )

    return p


def main() -> int:
    args = build_parser().parse_args()
    ds_range = (args.start, args.end)

    asyncio.run(
        render(
            ds_range=ds_range,
            base_url=args.base_url,
            headless=args.headless,
            outdir=args.outdir,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
