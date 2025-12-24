from PIL import Image
import aggdraw
import math
from typing import Tuple, Optional
from lambdawaker.draw.color.HSLuvColor import ColorUnion, to_hsluv_color, HSLuvColor

def create_radial_gradient(
    width: int = 800,
    height: int = 800,
    start_color: ColorUnion = (255, 255, 255, 255),
    end_color: ColorUnion = (0, 0, 0, 255),
    center: Optional[Tuple[float, float]] = None,
    radius: Optional[float] = None,
    step_size: float = 1.0,
) -> Image.Image:
    """
    Create an RGBA image and draw a radial gradient on it.

    Args:
        width (int): Width of the output image in pixels.
        height (int): Height of the output image in pixels.
        start_color (ColorUnion): The color at the center of the gradient.
        end_color (ColorUnion): The color at the outer edge of the gradient.
        center (Optional[Tuple[float, float]]): The center point (x, y) of the gradient.
                                                Defaults to the center of the image.
        radius (Optional[float]): The radius of the gradient. Defaults to the distance
                                  from the center to the farthest corner.
        step_size (float): The step size for drawing the concentric circles.

    Returns:
        PIL.Image.Image: The generated image containing the radial gradient.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = aggdraw.Draw(img)
    
    draw_radial_gradient(
        draw=draw,
        area_size=(width, height),
        start_color=start_color,
        end_color=end_color,
        center=center,
        radius=radius,
        step_size=step_size
    )
    
    draw.flush()
    return img

def draw_radial_gradient(
    draw: aggdraw.Draw,
    area_size: Tuple[int, int],
    start_color: ColorUnion = (255, 255, 255, 255),
    end_color: ColorUnion = (0, 0, 0, 255),
    center: Optional[Tuple[float, float]] = None,
    radius: Optional[float] = None,
    step_size: float = 1.0
) -> None:
    """
    Draws a radial gradient onto the given drawing context.

    Args:
        draw (aggdraw.Draw): The drawing context.
        area_size (Tuple[int, int]): The size of the area to fill (width, height).
        start_color (ColorUnion): The color at the center of the gradient.
        end_color (ColorUnion): The color at the outer edge of the gradient.
        center (Optional[Tuple[float, float]]): The center point (x, y) of the gradient.
                                                Defaults to the center of the area.
        radius (Optional[float]): The radius of the gradient. Defaults to the distance
                                  from the center to the farthest corner.
        step_size (float): The step size for drawing the concentric circles.
    """
    start_c = to_hsluv_color(start_color)
    end_c = to_hsluv_color(end_color)
    
    width, height = area_size
    
    if center is None:
        cx, cy = width / 2.0, height / 2.0
    else:
        cx, cy = center
        
    if radius is None:
        # Calculate distance to farthest corner
        corners = [(0, 0), (width, 0), (width, height), (0, height)]
        distances = [math.sqrt((x - cx)**2 + (y - cy)**2) for x, y in corners]
        max_radius = max(distances)
    else:
        max_radius = radius
        
    # Draw concentric circles from outside in to avoid gaps (though painter's algorithm works either way here)
    # Actually, drawing from outside in is better if we fill, but here we are stroking thick lines.
    # Let's iterate from 0 to max_radius.
    
    current_radius = max_radius
    while current_radius >= 0:
        # Calculate interpolation factor t in [0, 1]
        # t=0 at center (start_color), t=1 at max_radius (end_color)
        t = current_radius / max_radius
        t = max(0.0, min(1.0, t))
        
        # Interpolate HSLuv values
        h = start_c.hue + (end_c.hue - start_c.hue) * t
        s = start_c.saturation + (end_c.saturation - start_c.saturation) * t
        l = start_c.lightness + (end_c.lightness - start_c.lightness) * t
        a = start_c.alpha + (end_c.alpha - start_c.alpha) * t
        
        current_color = HSLuvColor(h, s, l, a)
        
        # Draw the circle
        # We use a pen with width slightly larger than step_size to ensure coverage
        pen = aggdraw.Pen(current_color.to_rgba(), step_size + 0.5)
        
        # aggdraw ellipse takes bounding box (x0, y0, x1, y1)
        x0 = cx - current_radius
        y0 = cy - current_radius
        x1 = cx + current_radius
        y1 = cy + current_radius
        
        draw.ellipse((x0, y0, x1, y1), pen)
        
        current_radius -= step_size
        
    draw.flush()
