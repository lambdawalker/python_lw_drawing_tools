import aggdraw
from PIL import Image
from typing import Tuple
from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color

def draw_squared_header(draw: aggdraw.Draw, height: int = 100, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Fills the top area of the canvas to create a header section.

    :param draw: The aggdraw.Draw object.
    :param height: The vertical distance from the top to fill.
    :param color: A tuple (R, G, B) or HSLuvColor.
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


def create_squared_header(
    width: int = 800,
    height: int = 400,
    header_height: int = 100,
    color: ColorUnion = (0, 0, 0, 255),
    bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an image and render a rectangular header on top.

    Args:
        width (int): Image width.
        height (int): Image height.
        header_height (int): Height of the filled header area from the top.
        color (ColorUnion): Fill color for the header.
        bg_color (ColorUnion): Background color (supports RGBA or HSLuvColor).

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_squared_header(draw=draw, height=header_height, color=color)
    draw.flush()
    return img


def create_square_header(
    width: int = 800,
    height: int = 400,
    header_height: int = 100,
    color: ColorUnion = (0, 0, 0, 255),
    bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """Alias for create_squared_header for convenience."""
    return create_squared_header(
        width=width,
        height=height,
        header_height=header_height,
        color=color,
        bg_color=bg_color,
    )
