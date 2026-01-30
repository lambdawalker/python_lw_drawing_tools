#!/usr/bin/env python3
import argparse
import asyncio
import traceback
from typing import Tuple

from lambdawaker.template.render.CardRenderer import CardRenderer


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
        error_message = traceback.format_exc()
        print(f"MESSAGE: Error during rendering: {error_message}")
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
        default="./output",
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
