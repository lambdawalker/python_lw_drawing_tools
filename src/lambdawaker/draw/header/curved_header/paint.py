import aggdraw
from PIL import Image
from typing import Union, Optional, Tuple

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.header.curved_header.parameters import generate_random_curved_header_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def draw_curved_header(draw: aggdraw.Draw, height: int = 100, curve_depth: float = 50, color: ColorUnion = (0, 0, 0, 255)) -> None:
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


def paint_random_curved_header(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        height: Union[int, Default, Random] = Default,
        curve_depth: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "height": height,
        "curve_depth": curve_depth,
        "color": color,
    })

    parameters = generate_random_curved_header_parameters(img, primary_color, color)

    parameters = parameters | passed_values
    
    draw = aggdraw.Draw(img)
    draw_curved_header(draw, **parameters)
