import bpy

from .image_type_conversion import create_blender_image


def assign_image_to_texture(mat, node_name, image):
    mat_ = mat

    if isinstance(mat, str):
        if mat not in bpy.data.materials:
            print(f"Material '{mat}' not found. Creating a new one.")
            return

        mat_ = bpy.data.materials[mat]

    if not mat_.use_nodes:
        print(f"Material '{mat}' does not use nodes.")
        return

    nodes = mat_.node_tree.nodes

    if node_name not in nodes:
        print(f"Node '{node_name}' not found in material '{mat}'.")
        return

    node = nodes[node_name]

    if node.type != 'TEX_IMAGE':
        print(f"Node '{node_name}' is not an image texture node.")
        return

    image = create_blender_image(image)

    node.image = image
    return image


def assign_image_to_world_node(world_name, node_name, image):
    if world_name not in bpy.data.worlds:
        print(f"World '{world_name}' not found.")
        return

    world = bpy.data.worlds[world_name]

    if not world.use_nodes:
        world.use_nodes = True

    nodes = world.node_tree.nodes

    if node_name not in nodes:
        print(f"Node '{node_name}' not found in world '{world_name}'.")
        return

    node = nodes[node_name]

    if node.type not in {'TEX_IMAGE', 'TEX_ENVIRONMENT'}:
        print(f"Node '{node_name}' is not a compatible texture node (Type: {node.type}).")
        return

    image = create_blender_image(image)
    node.image = image
    return image
