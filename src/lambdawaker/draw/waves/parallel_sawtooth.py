from PIL import Image
import math
import aggdraw
from typing import Tuple
from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color

def create_angled_sawtooth_waves(
    width: int = 800,
    height: int = 800,
    spacing: int = 50,
    thickness: float = 2,
    amplitude: float = 25,
    wavelength: float = 80,
    angle: float = 20,
    color: ColorUnion = (0, 0, 0, 255),
    bg_color: ColorUnion = (0, 0, 0, 0),
) -> Image.Image:
    """
    Create an RGBA image and draw rotated parallel sawtooth waves on it.

    This is a convenience wrapper around `draw_angled_sawtooth_waves` that
    allocates a new `PIL.Image.Image`, renders the waves using `aggdraw`, and
    returns the image.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        spacing (int): Distance between adjacent sawtooth baselines in pixels.
        thickness (float): Stroke thickness of the wave in pixels.
        amplitude (float): Peak vertical displacement of the sawtooth in pixels.
        wavelength (float): Horizontal length of one full tooth in pixels.
        angle (float): Rotation in degrees; positive values rotate
            counterclockwise around the image center.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.
        bg_color (ColorUnion): Background color for the created image as RGBA or HSLuvColor. Default
            is fully transparent black `(0, 0, 0, 0)`.

    Returns:
        PIL.Image.Image: The generated image containing the angled sawtooth waves.
    """
    color = to_hsluv_color(color)
    bg_color = to_hsluv_color(bg_color)

    img = Image.new("RGBA", (width, height), bg_color.to_rgba())
    draw = aggdraw.Draw(img)
    draw_angled_sawtooth_waves(
        draw=draw,
        area_size=(width, height),
        spacing=spacing,
        thickness=thickness,
        amplitude=amplitude,
        wavelength=wavelength,
        angle=angle,
        color=color,
    )
    draw.flush()
    return img


def draw_angled_sawtooth_waves(
    draw: aggdraw.Draw,
    area_size: Tuple[int, int],
    spacing: int = 50,
    thickness: float = 2,
    amplitude: float = 25,
    wavelength: float = 80,
    angle: float = 0,
    color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """
    Draw a set of parallel sawtooth waves at a given rotation into a context.

    Each wave is a zigzag (sawtooth) formed by alternating peaks and troughs
    spaced by `wavelength / 2`. The set of waves is rotated by `angle` degrees
    about the center and sized to cover the rectangular area after rotation.

    Args:
        draw (aggdraw.Draw): The drawing context to render into.
        area_size (tuple[int, int]): Target area as `(width, height)` in pixels.
        spacing (int): Distance between adjacent sawtooth baselines in pixels.
        thickness (float): Stroke thickness of the wave in pixels.
        amplitude (float): Peak vertical displacement of the sawtooth in pixels.
        wavelength (float): Horizontal length of one full tooth in pixels.
        angle (float): Rotation angle in degrees; positive values rotate
            counterclockwise.
        color (ColorUnion): Stroke color as an RGBA tuple or HSLuvColor.

    Returns:
        None: The drawing is rendered directly into `draw`.
    """
    color = to_hsluv_color(color)
    width, height = area_size
    pen = aggdraw.Pen(color.to_rgba(), thickness)

    rad = math.radians(angle)
    cx, cy = width / 2.0, height / 2.0

    # Ensure coverage of corners after rotation
    diagonal = int(math.sqrt(width ** 2 + height ** 2))

    # Step for alternating peak/trough points along the x-axis
    step = max(1, int(round(wavelength / 2.0)))

    for d in range(-diagonal, diagonal + int(spacing), int(spacing)):
        pts = []
        # Build a zigzag path far beyond the diagonal for full coverage
        for x_virtual in range(-diagonal - step, diagonal + step + 1, step):
            is_peak = ((x_virtual // step) % 2) == 0
            y_virtual = d + (amplitude if is_peak else -amplitude)

            # Rotate around center
            nx = x_virtual * math.cos(rad) - y_virtual * math.sin(rad) + cx
            ny = x_virtual * math.sin(rad) + y_virtual * math.cos(rad) + cy

            pts.extend([nx, ny])

        if len(pts) > 3:
            draw.line(pts, pen)

    draw.flush()

if __name__ == "__main__":
    create_angled_sawtooth_waves().show()
