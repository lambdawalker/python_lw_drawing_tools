import os
from io import BytesIO

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

        image_output_path = os.path.join(self.outdir, "../../assets/img", f"{record_id}_{template_name}.png")
        ensure_directory_for_file(image_output_path)
        canvas.save(image_output_path)
        return first_layer_image
