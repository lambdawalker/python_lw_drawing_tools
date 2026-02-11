import bpy


def get_scene_and_camera():
    scene = bpy.context.scene
    camera = scene.camera  # Ensure the scene has a camera
    return scene, camera
