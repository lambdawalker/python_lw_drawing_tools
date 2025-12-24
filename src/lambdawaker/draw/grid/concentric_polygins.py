import math
from typing import Tuple

import aggdraw
from PIL import Image


def create_concentric_polygons(
        width: int = 800,
        height: int = 800,
        sides: int = 6,
        rotation_step: float = 5,
        spacing: float = 15,
        color: Tuple[int, int, int, int] = (0, 0, 0, 255),
        thickness: float = 2,
        fill_opacity: int = 0,
        bg_color: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> Image.Image:
    """
    Create an RGBA image and draw concentric polygons on it.

    This is a convenience wrapper around `draw_concentric_polygons` that allocates a
    new `PIL.Image.Image`, draws the polygons using `aggdraw`, and returns the image.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        sides (int): Number of sides for the polygons (e.g., 6 for hexagons).
        rotation_step (float): Degrees of rotation added per nested layer.
        spacing (float): Pixel distance between each consecutive polygon.
        color (tuple): RGBA tuple for the outline color.
        thickness (float): Stroke thickness of polygon edges in pixels.
        fill_opacity (int): Alpha value for subtle fill (0-255; 0 is transparent).
        bg_color (tuple): Background color for the created image (RGBA; default transparent).

    Returns:
        PIL.Image.Image: The generated image containing the concentric polygons.
    """
    img = Image.new("RGBA", (width, height), bg_color)
    draw = aggdraw.Draw(img)

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


def draw_concentric_polygons(draw: aggdraw.Draw, canvas_size: Tuple[int, int], sides: int = 6, rotation_step: float = 5,
                             spacing: float = 15, color: Tuple[int, int, int, int] = (0, 0, 0, 255), thickness: float = 2, fill_opacity: int = 0) -> None:
    """
    Draws concentric polygons until the entire canvas is covered.

    Args:
        draw (aggdraw.Draw): The drawing context.
        canvas_size (tuple[int, int]): The size of the canvas (width, height).
        sides (int): Number of sides for the polygons.
        rotation_step (float): Degrees of rotation added per nested layer.
        spacing (float): Pixel distance between each consecutive polygon.
        color (tuple): RGBA tuple for the outline color.
        thickness (float): Stroke thickness of polygon edges in pixels.
        fill_opacity (int): Alpha value for subtle fill (0-255; 0 is transparent).
    """
    cx, cy = canvas_size[0] // 2, canvas_size[1] // 2

    # Calculate the distance to the furthest corner to ensure full coverage
    max_radius = math.sqrt(cx ** 2 + cy ** 2)
    num_polygons = int(1.5 * max_radius / spacing)

    for i in range(num_polygons, 0, -1):  # Draw from outside in for better layering
        radius = i * spacing
        angle_offset = math.radians(i * rotation_step)

        points = []
        for s in range(sides):
            angle = (2 * math.pi * s / sides) + angle_offset
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(x)
            points.append(y)

        # Optional: Add a subtle fill to create depth
        # Use the input color's RGB with custom alpha for fill
        fill_color = (color[0], color[1], color[2], fill_opacity)
        brush = aggdraw.Brush(fill_color)
        pen = aggdraw.Pen(color, thickness)

        draw.polygon(points, pen, brush)

    draw.flush()
