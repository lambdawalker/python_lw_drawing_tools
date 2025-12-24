import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color


def draw_curved_header(draw, height: int = 100, curve_depth: float = 50, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Creates a header with a curved bottom edge using aggdraw.path()
    """
    color = to_hsluv_color(color)
    width, _ = draw.size
    brush = aggdraw.Brush(color.to_rgba())

    # 1. Define the Path coordinates/commands
    # aggdraw.Path() accepts a list of coordinates or a symbol string,
    # but we can also use its methods.
    path = aggdraw.Path()
    path.moveto(0, 0)
    path.lineto(width, 0)
    path.lineto(width, height)

    # Use qcurveto for the 4-parameter quadratic curve
    # (control_x, control_y, end_x, end_y)
    # Arguments: (ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
    path.curveto(width * 0.75, height + curve_depth, width * 0.25, height + curve_depth, 0, height)
    path.close()

    # 2. DRAW the path using the canvas object
    # The syntax is: canvas.path(path, pen_or_brush)
    # Or: canvas.path(path_string, pen, brush)
    draw.path(path, brush)

    # 3. Flush to the PIL image
    draw.flush()


def create_curved_header(
        width: int = 800,
        height: int = 400,
        header_height: int = 100,
        curve_depth: float = 50,
        color: ColorUnion = (0, 0, 0, 255),
        bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an image and render a curved header on top.

    Args:
        width (int): Image width.
        height (int): Image height.
        header_height (int): Vertical position where the curve meets the sides.
        curve_depth (int|float): How far the curve dips below the header_height.
        color (ColorUnion): Fill color for the header as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color (RGBA or HSLuvColor).

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_curved_header(draw=draw, height=header_height, curve_depth=curve_depth, color=color)
    draw.flush()
    return img
