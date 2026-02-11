import sys

import bpy
import mathutils

from ..console_input import ask_for_range


def build_parameter_description(socket, value, min_value=None, max_value=None, purpose=None):
    param_type = type(value).__name__

    if isinstance(value, bpy.types.bpy_prop_array):
        value = tuple(value)
        param_type = 'list'

    if isinstance(value, mathutils.Euler):
        value = tuple(value)
        param_type = 'list'

    result = {
        'name': socket.name,
        'defaultValue': value,
        'inputType': param_type,
        'purpose': purpose
    }

    if isinstance(value, tuple):
        param_type = type(value[0]).__name__
        result['subType'] = param_type

    randomize_value = ask_for_range(socket.name, min_value=min_value, max_value=max_value, purpose=purpose)

    result.update(randomize_value)
    return result


def query_nodes_parameters(material_name, nodes_name=None):
    nodes_name = nodes_name if nodes_name is not None else ["Main"]
    material = bpy.data.materials.get(material_name)
    nodes = material.node_tree.nodes

    nodes_data = []
    for name in nodes_name:
        node = nodes[name]
        nodes_data.append(
            query_node_parameters(node)
        )

    return {
        "name": material.name,
        "nodes": nodes_data
    }


def query_node_parameters(node):
    inputs = []
    outputs = []

    interfaces = {}

    if node.type == "GROUP":
        interfaces = node.node_tree.interface.items_tree

    # List all input parameters of the connected node
    for input_socket in node.inputs:
        if hasattr(input_socket, 'default_value'):
            interface = interfaces.get(input_socket.name)

            inputs.append(
                build_parameter_description(
                    input_socket,
                    interface.default_value if interface is not None else None,
                    interface.min_value if interface is not None and hasattr(interface, "min_value") else None,
                    interface.max_value if interface is not None and hasattr(interface, "max_value") else None,
                    interface.subtype if interface is not None and hasattr(interface, "subtype") else None
                )
            )

    # List all output parameters of the connected node
    for output_socket in node.outputs:
        if hasattr(output_socket, 'default_value'):
            outputs.append(
                build_parameter_description(
                    output_socket,
                    output_socket.default_value
                )
            )

    return {
        "name": node.name,
        "inputs": inputs,
        "outputs": outputs
    }


def output_surface_node(material):
    if material is None:
        raise Exception(f"Material '{material.name}' not found.")

    if not material.use_nodes:
        raise Exception(f"Material '{material.name}' does not use nodes.")

    node_tree = material.node_tree
    nodes = node_tree.nodes

    material_output_node = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            material_output_node = node
            break

    if material_output_node is None:
        raise Exception(f"No material output node found in material '{material.name}'.")

    target_node = None

    for input_socket in material_output_node.inputs:
        if not input_socket.is_linked or input_socket.name != "Surface":
            continue

        target_node = input_socket.links[0].from_node
        break

    if target_node is None:
        raise Exception(f"No node connected to the material output node in material '{material.name}'.")

    return target_node


def search_value(obj, target, path="", seen=None, current_depth=0):
    if seen is None:
        seen = set()

    # Check if current depth exceeds recursion limit
    if current_depth > sys.getrecursionlimit() - 10:  # Keeping a buffer to avoid hitting the limit exactly
        return

    obj_id = id(obj)
    if obj_id in seen:
        return
    seen.add(obj_id)

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}/{key}" if path else key
            if value == target:
                print(f">>> {new_path} {value}")
            search_value(value, target, new_path, seen, current_depth + 1)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            new_path = f"{path}/{index}" if path else str(index)
            if value == target:
                print(f">>> {new_path} {value}")
            search_value(value, target, new_path, seen, current_depth + 1)
    else:
        if obj == target:
            print(path)
        else:
            for attr in dir(obj):
                if attr.startswith('_'):
                    continue
                try:
                    attr_value = getattr(obj, attr)
                    new_path = f"{path}.{attr}" if path else attr
                    if attr_value == target:
                        print(f">>> {new_path} {attr_value}")
                    search_value(attr_value, target, new_path, seen, current_depth + 1)
                except AttributeError:
                    continue
