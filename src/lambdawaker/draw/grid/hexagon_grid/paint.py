import math
from typing import Tuple, Union, Optional

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.hexagon_grid.parameters import generate_random_hexagon_grid_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_hexagon_grid(
        image: Image.Image,
        area_size: Optional[Tuple[int, int]] = None,
        hexagon_size: float = 50,
        thickness: float = 2.0,
        angle: float = 0,
        color: ColorUnion = (0, 0, 0, 255),
) -> None:
    """
    Draw a hexagon tiling across a given area onto an existing image.
    """
    color = to_hsluv_color(color)

    if area_size is None:
        area_size = image.size

    draw = aggdraw.Draw(image)
    width, height = area_size
    pen = aggdraw.Pen(color.to_rgba(), thickness)

    cx, cy = width / 2, height / 2
    rad_rotation = math.radians(angle)

    # Hexagon Math: Width and Height of a single hexagon
    hex_width = 2 * hexagon_size
    hex_height = math.sqrt(3) * hexagon_size

    # Horizontal and Vertical spacing for tiling
    horiz_dist = hex_width * 3 / 4
    vert_dist = hex_height

    # Calculate diagonal to ensure full coverage during rotation
    diagonal = int(math.sqrt(width ** 2 + height ** 2))

    # helper for rotation
    def rotate_point(px, py):
        # Translate to origin, rotate, translate back
        tx, ty = px - cx, py - cy
        rx = tx * math.cos(rad_rotation) - ty * math.sin(rad_rotation) + cx
        ry = tx * math.sin(rad_rotation) + ty * math.cos(rad_rotation) + cy
        return rx, ry

    # Iterate through a grid large enough to cover the diagonal
    for col in range(-diagonal // int(horiz_dist) - 2, diagonal // int(horiz_dist) + 2):
        for row in range(-diagonal // int(vert_dist) - 2, diagonal // int(vert_dist) + 2):

            # Calculate center of current hexagon
            # Offset every other column
            x_offset = col * horiz_dist
            y_offset = row * vert_dist
            if col % 2 != 0:
                y_offset += vert_dist / 2

            # Draw the 6 sides
            points = []
            for i in range(7):  # 7 points to close the loop
                # Calculate vertex relative to grid origin (0,0) before rotation
                angle_deg = 60 * i
                angle_rad = math.radians(angle_deg)

                px = x_offset + hexagon_size * math.cos(angle_rad)
                py = y_offset + hexagon_size * math.sin(angle_rad)

                # Apply global grid rotation
                rx, ry = rotate_point(px, py)
                points.extend([rx, ry])

            draw.line(points, pen)

    draw.flush()


def paint_random_hexagon_grid(
        img: Image.Image,
        primary_color: Union[ColorUnion, Random] = Random,
        color: Optional[ColorUnion] = Default,
        size: Union[Tuple[int, int], Default, Random] = Default,
        hexagon_size: Union[float, Default, Random] = Default,
        thickness: Union[float, Default, Random] = Default,
        angle: Union[float, Default, Random] = Default,
) -> None:
    passed_values = clean_passed_parameters({
        "area_size": size,
        "hexagon_size": hexagon_size,
        "thickness": thickness,
        "angle": angle,
        "color": color,
    })

    parameters = generate_random_hexagon_grid_parameters(img, primary_color, color, size)

    parameters = parameters | passed_values
    paint_hexagon_grid(img, **parameters)
