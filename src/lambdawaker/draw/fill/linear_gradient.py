from PIL import Image
import aggdraw
import math
from typing import Tuple
from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color, HSLuvColor

def create_gradient(
    width: int = 800,
    height: int = 800,
    start_color: ColorUnion = (0, 0, 0, 255),
    end_color: ColorUnion = (255, 255, 255, 255),
    angle: float = 0,
    step_size: float = 1.0,
) -> Image.Image:
    """
    Create an RGBA image and draw a linear gradient on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        start_color (ColorUnion): The starting color of the gradient.
        end_color (ColorUnion): The ending color of the gradient.
        angle (float): The angle of the gradient in degrees.
        step_size (float): The step size for drawing the gradient lines.

    Returns:
        PIL.Image.Image: The generated image containing the gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = aggdraw.Draw(img)
    
    draw_gradient(
        draw=draw,
        area_size=(width, height),
        start_color=start_color,
        end_color=end_color,
        angle=angle,
        step_size=step_size
    )
    
    draw.flush()
    return img

def draw_gradient(
    draw: aggdraw.Draw,
    area_size: Tuple[int, int],
    start_color: ColorUnion = (0, 0, 0, 255),
    end_color: ColorUnion = (255, 255, 255, 255),
    angle: float = 0,
    step_size: float = 1.0
) -> None:
    """
    Draws a linear gradient onto the given drawing context.

    Args:
        draw (aggdraw.Draw): The drawing context.
        area_size (Tuple[int, int]): The size of the area to fill (width, height).
        start_color (ColorUnion): The starting color of the gradient.
        end_color (ColorUnion): The ending color of the gradient.
        angle (float): The angle of the gradient in degrees.
        step_size (float): The step size for drawing the gradient lines.
    """
    start_c = to_hsluv_color(start_color)
    end_c = to_hsluv_color(end_color)
    
    width, height = area_size
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    # Calculate the projection of the 4 corners onto the gradient vector
    corners = [
        (0, 0),
        (width, 0),
        (width, height),
        (0, height)
    ]
    
    projections = [x * cos_a + y * sin_a for x, y in corners]
    min_proj = min(projections)
    max_proj = max(projections)
    length = max_proj - min_proj
    
    if length == 0:
        length = 1.0
        
    # Diagonal length to ensure lines cover the width perpendicular to gradient
    diagonal = math.sqrt(width**2 + height**2)
    
    # Iterate through the gradient range
    current_proj = min_proj
    while current_proj <= max_proj + step_size:
        # Calculate interpolation factor t in [0, 1]
        t = (current_proj - min_proj) / length
        t = max(0.0, min(1.0, t))
        
        # Interpolate HSLuv values
        h = start_c.hue + (end_c.hue - start_c.hue) * t
        s = start_c.saturation + (end_c.saturation - start_c.saturation) * t
        l = start_c.lightness + (end_c.lightness - start_c.lightness) * t
        a = start_c.alpha + (end_c.alpha - start_c.alpha) * t
        
        current_color = HSLuvColor(h, s, l, a)
        
        # Calculate the center point on the gradient line
        cx = current_proj * cos_a
        cy = current_proj * sin_a
        
        # Calculate start and end points of the perpendicular line
        # Perpendicular vector is (-sin_a, cos_a)
        x0 = cx - diagonal * (-sin_a)
        y0 = cy - diagonal * cos_a
        x1 = cx + diagonal * (-sin_a)
        y1 = cy + diagonal * cos_a
        
        # Draw the line
        # Add a small overlap to step_size to avoid gaps
        pen = aggdraw.Pen(current_color.to_rgba(), step_size + 0.5)
        draw.line((x0, y0, x1, y1), pen)
        
        current_proj += step_size
        
    draw.flush()
