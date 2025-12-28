import aggdraw
from PIL import Image
from typing import Union, Optional

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.square_header.parameters import generate_random_square_header_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def draw_squared_header(draw: aggdraw.Draw, height: int = 100, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Fills the top area of the canvas to create a header section.
    """
    color = to_hsluv_color(color)
    # Create a Brush for the fill.
    # aggdraw uses (opacity, R, G, B) for color arguments in the Brush.
    brush = aggdraw.Brush(color.to_rgba())

    # Define the coordinates for the header rectangle: (x0, y0, x1, y1)
    # We get the width from the canvas's internal surface if needed,
    # but drawing past the edge is safe in aggdraw.
    width = draw.size[0]

    # Draw the rectangle (no Pen/outline needed for a simple fill)
    draw.rectangle((0, 0, width, height), brush)

    # Ensure the drawing is flushed to the image buffer
    draw.flush()


def paint_random_square_header(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        height: Union[int, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "height": height,
        "color": color,
    })

    parameters = generate_random_square_header_parameters(img, primary_color, color)

    parameters = parameters | passed_values
    
    draw = aggdraw.Draw(img)
    draw_squared_header(draw, **parameters)
