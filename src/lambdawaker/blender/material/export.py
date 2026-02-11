import json
import os

from .query import query_nodes_parameters


def export_node_parameters(material_name, nodes_name=None, directory="./"):
    nodes_name = ["Surface"] if nodes_name is None else nodes_name

    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, f"{material_name}.json")

    node_parameters = query_nodes_parameters(material_name, nodes_name)

    with open(file_path, 'w') as json_file:
        json.dump(node_parameters, json_file, indent=4)

    print(f"Material data saved to {file_path}")
