import random

import aggdraw
from PIL import Image

from lambdawaker.draw import fill as fill_module
from lambdawaker.draw import grid as grid_module
from lambdawaker.draw import header
from lambdawaker.draw.color.HSLuvColor import random_alpha
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.fill.linear_gradient.paint import paint_random_linear_gradient
from lambdawaker.draw.grid.concentric_polygons.paint import paint_random_concentric_polygons
from lambdawaker.draw.shapes import simple_shapes
from lambdawaker.reflection.query import select_random_function_from_module, select_random_function_from_module_and_submodules

if __name__ == "__main__":
    primary_color = generate_hsluv_text_contrasting_color()
    shape = select_random_function_from_module(simple_shapes)

    width = 800
    height = 600

    radius = random.randint(5, 15)
    separation = radius * random.uniform(1.3, 1.5)
    angle = random.uniform(0, 360)
    thickness = random.uniform(0.5, 5)
    accent_stroke_color = primary_color.close_color() - random_alpha(.2, .8)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    background_paint_function = select_random_function_from_module_and_submodules(fill_module, "paint_random_.*")

    paint_random_linear_gradient(
        img,
        primary_color=primary_color,
    )

    background_details = select_random_function_from_module_and_submodules(grid_module, "paint_random_.*")

    paint_random_concentric_polygons(
        img,
        primary_color=primary_color
    )

    draw = aggdraw.Draw(img)
    header_draw_function = select_random_function_from_module_and_submodules(
        header,
        name_pattern="draw_.*"
    )


    header_draw_function(
        draw,
        150,
        color=primary_color.harmonious_color() - random_alpha(0, .7)
    )

    img.show()
