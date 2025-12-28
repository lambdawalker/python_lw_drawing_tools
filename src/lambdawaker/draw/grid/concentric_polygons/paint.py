import math
from typing import Tuple, Union, Optional, Dict, Any

import aggdraw
from PIL import Image

from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color
from lambdawaker.draw.grid.concentric_polygons.parameters import generate_random_concentric_polygons_parameters
from lambdawaker.random.values import Random, Default, clean_passed_parameters


def paint_concentric_polygons(
    image: Image.Image,
    canvas_size: Optional[Tuple[int, int]] = None,
    sides: int = 6,
    rotation_step: float = 5,
    spacing: float = 15,
    color: ColorUnion = (0, 0, 0, 255),
    thickness: float = 2,
    fill_opacity: int = 0
) -> None:
    """
    Draws concentric polygons onto an existing PIL image using aggdraw.

    Args:
        image (Image.Image): The PIL Image object to draw on.
        canvas_size (Optional[Tuple[int, int]]): The size of the canvas (width, height).
                                                  If None, uses the image's size.
        sides (int): The number of sides for each polygon.
        rotation_step (float): The angular rotation step in degrees between consecutive polygons.
        spacing (float): The radial distance between consecutive polygons.
        color (ColorUnion): The color of the polygon outlines. Can be an HSLuvColor object,
                            a tuple (h, s, l, a) for HSLuv, or (r, g, b, a) for RGBA.
        thickness (float): The thickness of the polygon outlines.
        fill_opacity (int): The opacity (0-255) of the polygon fill. If 0, polygons are not filled.

    Returns:
        None: The drawing is performed directly on the provided `image` object.
    """
    color = to_hsluv_color(color)
    
    if canvas_size is None:
        canvas_size = image.size

    draw = aggdraw.Draw(image)
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
        rgba = color.to_rgba()
        fill_color = (rgba[0], rgba[1], rgba[2], fill_opacity)
        brush = aggdraw.Brush(fill_color)
        pen = aggdraw.Pen(rgba, thickness)

        draw.polygon(points, pen, brush)

    draw.flush()


def paint_random_concentric_polygons(
    img: Image.Image,
    size: Union[Tuple[int, int], Default, Random] = Default,
    sides: Union[int, Default, Random] = Default,
    rotation_step: Union[float, Default, Random] = Default,
    spacing: Union[float, Default, Random] = Default,
    color: Optional[ColorUnion] = None,
    thickness: Union[float, Default, Random] = Default,
    fill_opacity: Union[int, Default, Random] = Default
) -> None:
    """
    Generates random parameters for concentric polygons and draws them onto a PIL image.

    Args:
        img (Image.Image): The PIL Image object to draw on.
        size (Union[Tuple[int, int], Default, Random]): The canvas size (width, height).
                                                        Can be a specific tuple, Default to use
                                                        image size, or Random to generate randomly.
        sides (Union[int, Default, Random]): The number of sides for polygons.
                                             Can be a specific int, Default, or Random.
        rotation_step (Union[float, Default, Random]): The rotation step in degrees.
                                                       Can be a specific float, Default, or Random.
        spacing (Union[float, Default, Random]): The radial spacing between polygons.
                                                 Can be a specific float, Default, or Random.
        color (Optional[ColorUnion]): The base color for polygons. If None, a random color is generated.
        thickness (Union[float, Default, Random]): The thickness of polygon outlines.
                                                   Can be a specific float, Default, or Random.
        fill_opacity (Union[int, Default, Random]): The opacity (0-255) of the polygon fill.
                                                    Can be a specific int, Default, or Random.

    Returns:
        None: The drawing is performed directly on the provided `img` object.
    """
    passed_values = clean_passed_parameters({
        "canvas_size": size,
        "sides": sides,
        "rotation_step": rotation_step,
        "spacing": spacing,
        "color": color,
        "thickness": thickness,
        "fill_opacity": fill_opacity,
    })

    parameters = generate_random_concentric_polygons_parameters(img, size)

    parameters = parameters | passed_values
    paint_concentric_polygons(img, **parameters)
