import bpy


def query_vertices_world_vector_in_vertex_group(obj, group_name):
    if isinstance(obj, str):
        obj = bpy.data.objects.get(obj)

    if obj is None:
        raise Exception("Object is null")

    # Ensure object has vertices
    if obj.type != 'MESH' or obj.data is None:
        raise Exception("Object is not a Mesh")

    # Get the vertex group
    vertex_group = obj.vertex_groups.get(group_name)

    if vertex_group is None:
        print(f"Vertex group '{group_name}' not found in object '{obj}'.")
        return []

    # Get the indices of vertices in the vertex group
    vertices_indices = [v.index for v in obj.data.vertices if vertex_group.index in [vg.group for vg in v.groups]]

    # Transform vertices to world space
    world_vertices = []
    for index in vertices_indices:
        vertex = obj.data.vertices[index]
        world_vertex = obj.matrix_world @ vertex.co
        world_vertices.append(world_vertex.copy())

    # Return the vertices in world space
    return world_vertices
