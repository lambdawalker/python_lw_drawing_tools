from typing import Union

import bpy


def set_material_to_mesh(
        obj_name: str,
        mat: Union[str, bpy.types.Material],
        slot_index: int | None = None,
        assign_to_all_faces: bool = False
) -> bpy.types.Material:
    """
    Assign a material (by name) to a mesh object (by name).

    Parameters
    ----------
    obj_name : str
        Name of the object in the scene (must be type 'MESH').
    mat : str
        Name of the material datablock.
    create_if_missing : bool
        If True, create the material if it doesn't exist.
    slot_index : int | None
        If None, uses the first slot if exists, else appends.
        If int, ensures that slot exists and sets it.
    assign_to_all_faces : bool
        If True, assigns the material to all polygons (enters edit mode).

    Returns
    -------
    bpy.types.Material
        The assigned material.

    Raises
    ------
    ValueError
        If object not found, wrong type, or material missing (and not creating).
    """

    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        raise ValueError(f"Object '{obj_name}' not found.")

    if obj.type != 'MESH' or obj.data is None:
        raise ValueError(f"Object '{obj_name}' is not a mesh.")

    mat_ = mat
    if isinstance(mat, str):
        mat_ = bpy.data.materials.get(mat)

    if mat_ is None:
        raise ValueError(f"Material '{mat}' not found.")

    mats = obj.data.materials

    if slot_index is None:
        if len(mats) == 0:
            mats.append(mat_)
            slot_index = 0
        else:
            mats[0] = mat_
            slot_index = 0
    else:
        if slot_index < 0:
            raise ValueError("slot_index must be >= 0")
        while len(mats) <= slot_index:
            mats.append(None)
        mats[slot_index] = mat_

    # Optionally assign to all faces (material_index per polygon)
    if assign_to_all_faces:
        if bpy.context.object != obj:
            bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Enter edit mode, select all, assign material
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        obj.active_material_index = slot_index
        bpy.ops.object.material_slot_assign()
        bpy.ops.object.mode_set(mode='OBJECT')

    return mat_
