import bpy
import bpy_extras
from mathutils import Vector


def compute_obj_pixel_bounding_box(scene, obj, camera):
    if isinstance(obj, str):
        obj = bpy.data.objects.get(obj)

    # Ensure the object is in the scene
    if obj.name not in scene.objects:
        raise ValueError(f"Object {obj.name} is not in the scene {scene.name}")

    # Get the 3D bounding box of the object
    bbox_corners = [
        obj.matrix_world @ Vector(corner) for corner in obj.bound_box
    ]

    return compute_vectors_pixel_bounding_box(scene, bbox_corners, camera)


def compute_vectors_pixel_bounding_box(scene, vectors, camera):
    # Ensure the camera is in the scene
    if camera.name not in scene.objects:
        raise ValueError(f"Camera {camera.name} is not in the scene {scene.name}")

    # Get the render resolution and scale
    render = scene.render
    render_scale = render.resolution_percentage / 100.0
    render_size = Vector((render.resolution_x * render_scale, render.resolution_y * render_scale))

    # Convert the bounding box corners to 2D screen coordinates
    screen_corners = [
        bpy_extras.object_utils.world_to_camera_view(
            scene, camera, Vector(corner)
        )
        for corner in vectors
    ]

    # Find the min and max coordinates in 2D screen space
    min_x = min(corner.x for corner in screen_corners)
    max_x = max(corner.x for corner in screen_corners)
    min_y = min(corner.y for corner in screen_corners)
    max_y = max(corner.y for corner in screen_corners)

    # Convert normalized coordinates to pixel coordinates
    min_x_px = int(min_x * render_size.x)
    max_x_px = int(max_x * render_size.x)
    min_y_px = int(render_size.y - max_y * render_size.y)
    max_y_px = int(render_size.y - min_y * render_size.y)

    return min_x_px, min_y_px, max_x_px, max_y_px


def create_plane_from_vertices(vertices, plane_name="Indicator"):
    """
    Create a plane in Blender given 4 vertices as a tuple of tuples.

    Args:
        vertices (tuple): A tuple of 4 tuples, each containing 3 coordinates (x, y, z).
        plane_name (str): The name of the new plane object.

    Returns:
        bpy.types.Object: The newly created plane object.
    """
    if len(vertices) != 4:
        raise ValueError("Exactly 4 vertices are required to create a plane.")

    vertices = [Vector(vertex) for vertex in vertices]

    mesh = bpy.data.meshes.new(plane_name + "Mesh")
    plane = bpy.data.objects.new(plane_name, mesh)

    bpy.context.collection.objects.link(plane)
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()

    return plane
