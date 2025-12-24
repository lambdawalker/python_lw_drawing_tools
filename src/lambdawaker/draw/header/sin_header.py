import aggdraw
import math
from PIL import Image
from typing import Tuple
from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color

def draw_sine_header(draw: aggdraw.Draw, height: int = 100, amplitude: float = 20, frequency: float = 2, color: ColorUnion = (0, 0, 0, 255)) -> None:
    """
    Creates a header with a sine-wave bottom edge.

    :param draw: The aggdraw.Draw object.
    :param height: The vertical center point of the wave.
    :param amplitude: The height of the wave peaks.
    :param frequency: How many full waves span the width.
    :param color: Tuple (R, G, B, A) or HSLuvColor.
    """
    color = to_hsluv_color(color)
    width, _ = draw.size
    brush = aggdraw.Brush(color.to_rgba())
    path = aggdraw.Path()

    # 1. Start at top-left and go to top-right
    path.moveto(0, 0)
    path.lineto(width, 0)

    # 2. Draw the right-side vertical edge down to the start of the wave
    # We calculate the Y for the sine wave at the far right edge
    end_y = height + amplitude * math.sin(2 * math.pi * frequency)
    path.lineto(width, end_y)

    # 3. Trace the Sine wave from right to left (back to x=0)
    # The more steps, the smoother the curve appears.
    steps = 100
    for i in range(steps, -1, -1):
        x = (i / steps) * width
        # Sine formula: y = baseline + amplitude * sin(2 * PI * freq * (x/width))
        y = height + amplitude * math.sin(2 * math.pi * frequency * (i / steps))
        path.lineto(x, y)

    # 4. Close the path (returns to 0,0)
    path.close()

    # 5. Render onto canvas
    draw.path(path, brush)
    draw.flush()


def create_sine_header(
    width: int = 800,
    height: int = 400,
    header_height: int = 100,
    amplitude: float = 20,
    frequency: float = 2,
    color: ColorUnion = (0, 0, 0, 255),
    bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an image and render a sine-wave header on top.

    Args:
        width (int): Image width.
        height (int): Image height.
        header_height (int): Vertical position of the wave baseline.
        amplitude (float): Wave amplitude in pixels.
        frequency (float): Number of full waves across the width.
        color (ColorUnion): Fill color for the header (RGBA tuple or HSLuvColor).
        bg_color (ColorUnion): Background color (RGBA tuple or HSLuvColor).

    Returns:
        PIL.Image.Image: The generated image.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_sine_header(
        draw=draw,
        height=header_height,
        amplitude=amplitude,
        frequency=frequency,
        color=color,
    )
    draw.flush()
    return img
