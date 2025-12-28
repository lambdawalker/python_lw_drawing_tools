import random

import aggdraw
from PIL import Image

from lambdawaker.draw import fill as fill_module
from lambdawaker.draw import header
from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color, random_alpha
from lambdawaker.draw.color.generate_color import generate_hsluv_text_contrasting_color
from lambdawaker.draw.fill.linear_gradient.paint import paint_random_linear_gradient
from lambdawaker.draw.grid import simple_shapes
from lambdawaker.draw.grid.concentric_polygins import draw_concentric_polygons
from lambdawaker.draw.grid.shapes_grid import draw_shapes_grid
from lambdawaker.reflection.query import select_random_function_from_module, select_random_function_from_module_and_submodules


def create_type_a_card_background(width=800, height=800, primary_color: ColorUnion = (100, 100, 0, 255)):
    primary_color = to_hsluv_color(primary_color)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = aggdraw.Draw(img)

    sides = random.randint(3, 12)
    rotation_step = random.uniform(0, 15)
    spacing = random.randint(10, 50)
    thickness = random.uniform(1, 5)
    fill_opacity = random.randint(0, 100)

    draw_concentric_polygons(
        draw=draw,
        canvas_size=(width, height),
        sides=sides,
        rotation_step=rotation_step,
        spacing=spacing,
        color=primary_color,
        thickness=thickness,
        fill_opacity=fill_opacity,
    )

    return img


if __name__ == "__main__":
    primary_color = generate_hsluv_text_contrasting_color()
    shape = select_random_function_from_module(simple_shapes)

    width = 800
    height = 600

    radius = random.randint(5, 15)
    separation = radius * random.uniform(1.3, 1.5)
    angle = random.uniform(0, 360)
    thickness = random.uniform(0.5, 5)
    outline = primary_color.harmonious_color()

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    background_paint_function = select_random_function_from_module_and_submodules(fill_module, "paint_random_.*")

    paint_random_linear_gradient(
        img
    )

    draw = aggdraw.Draw(img)
    draw_shapes_grid(
        draw,
        img.size,
        radius=radius,
        draw_function=shape,
        separation=separation,
        angle=angle,
        thickness=thickness,
        color=primary_color.close_color() - random_alpha(.5, .9),
        outline=outline - random_alpha(.5, .9)
    )

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
    img.save("t.png")
