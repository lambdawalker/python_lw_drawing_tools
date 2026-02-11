import os

import bpy


def render_scene(output_path, resolution_x=800, resolution_y=800, file_format='JPEG', color_depth='8'):
    """
    Renders the current scene to the specified output file.

    Parameters:
        output_path (str): The file path to save the rendered image.
        resolution_x (int): The horizontal resolution of the render.
        resolution_y (int): The vertical resolution of the render.
        file_format (str): The file format of the output image (e.g., 'PNG', 'JPEG').
        color_depth (str): The color depth of the output image (e.g., '8', '16').
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set the render resolution
    if resolution_x is not None:
        bpy.context.scene.render.resolution_x = resolution_x
    if resolution_y is not None:
        bpy.context.scene.render.resolution_y = resolution_y

    # Set the output file format
    bpy.context.scene.render.image_settings.file_format = file_format

    # Set the color depth
    bpy.context.scene.render.image_settings.color_depth = color_depth

    # Set the output file path
    bpy.context.scene.render.filepath = output_path

    print(f"    Rendering with {bpy.context.scene.render.engine}")
    # Perform the rendering
    bpy.ops.render.render(write_still=True)
