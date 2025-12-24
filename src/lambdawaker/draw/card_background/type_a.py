import inspect
import random
import re

import aggdraw
from PIL import Image

from lambdawaker.draw import header
from lambdawaker.draw.grid import simple_shapes
from lambdawaker.draw.grid.concentric_polygins import draw_concentric_polygons
from lambdawaker.draw.grid.shapes_grid import create_shapes_grid


def create_type_a_card_background(width=800, height=800, primary_color=(100, 100, 0, 255)):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = aggdraw.Draw(img)

    sides = random.randint(3, 12)
    rotation_step = random.uniform(0, 15)
    spacing = random.randint(10, 50)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 20)
    thickness = random.uniform(1, 5)
    fill_opacity = random.randint(0, 100)

    draw_concentric_polygons(
        draw=draw,
        canvas_size=(width, height),
        sides=sides,
        rotation_step=rotation_step,
        spacing=spacing,
        color=color,
        thickness=thickness,
        fill_opacity=fill_opacity,
    )

    return img


def select_random_function_from_module(module, name_pattern=None):
    """
    Given a module, selects a random function from that module.

    Args:
        module: A Python module object
        name_pattern: Optional regexp pattern to filter functions by name

    Returns:
        A randomly selected function from the module

    Raises:
        ValueError: If no functions are found in the module
    """
    functions = [obj for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]

    if name_pattern is not None:
        pattern = re.compile(name_pattern)
        functions = [func for func in functions if pattern.search(func.__name__)]

    if not functions:
        raise ValueError(f"No functions found in module {module.__name__}")

    return random.choice(functions)


if __name__ == "__main__":
    shape = select_random_function_from_module(simple_shapes)

    print(shape)

    width = 800
    height = 600

    radius = random.randint(5, 50)
    separation = random.randint(0, 30)
    angle = random.uniform(0, 360)
    thickness = random.uniform(0.5, 5)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(50, 255))
    outline = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(50, 255))

    base = create_shapes_grid(
        width=width,
        height=height,
        radius=radius,
        draw_function=shape,
        separation=separation,
        angle=angle,
        thickness=thickness,
        color=color,
        outline=outline
    )

    header_draw_function = select_random_function_from_module(header, name_pattern="draw_.*")

    draw = aggdraw.Draw(base)
    header_draw_function(draw, 200)

    base.show()
