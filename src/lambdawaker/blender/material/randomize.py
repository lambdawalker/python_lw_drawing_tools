import bpy
import json
import random
import colorsys
import math
import zlib


def randomize_material(material, seed=None):
    """
    A completely standalone function to randomize a Blender material
    based on JSON data stored in 'mrp_internal_preset_json'.

    Args:
        material (bpy.types.Material or str): The material object or the name of the material.
        seed (int, optional): An override seed. If None, uses the seed stored in JSON or a random one.
    """

    # --- Internal Helper Logic (Self-Contained) ---

    def get_stable_hash(s):
        return zlib.crc32(s.encode('utf-8')) & 0xffffffff

    def get_random_value(min_val, max_val, dist_type, seed_val):
        random.seed(seed_val)
        real_min, real_max = min(min_val, max_val), max(min_val, max_val)

        if dist_type == 'GAUSSIAN':
            mu = (real_min + real_max) / 2
            sigma = (real_max - real_min) / 6
            return max(real_min, min(random.gauss(mu, sigma), real_max))
        elif dist_type == 'STEPPED':
            steps = 5
            if real_max == real_min: return real_min
            step_val = (real_max - real_min) / steps
            return real_min + (round(random.random() * steps) * step_val)
        return random.uniform(real_min, real_max)

    # --- Pre-flight Checks ---

    # Check if material is a string (name)
    if isinstance(material, str):
        material = bpy.data.materials.get(material)

    if not material:
        print("Error: Material not found or invalid.")
        return

    if "mrp_internal_preset_json" not in material:
        print(f"No Randomizer Pro data found on material: {material.name}")
        return

    try:
        data = json.loads(material["mrp_internal_preset_json"])
    except Exception as e:
        print(f"Failed to parse JSON on material {material.name}: {e}")
        return

    # Determine the base seed: Priority is Argument > JSON > Random
    if seed is not None:
        base_seed = seed
    else:
        base_seed = data.get("seed", random.randint(0, 999999))

    nodes_data = data.get("nodes", {})

    if not material.node_tree:
        return

    nodes = material.node_tree.nodes

    for node_name, node_cfg in nodes_data.items():
        node = nodes.get(node_name)
        if not node or not node_cfg.get("enabled", False):
            continue

        # Calculate unique seed for this node
        node_id_hash = get_stable_hash(node.name)
        local_offset = node_cfg.get("seed_off", 0)
        node_seed = base_seed + (node_id_hash * 31) + local_offset

        # 1. Handle Special Node Types (ColorRamps)
        if node.type == 'VALTORGB':
            ramp = node.color_ramp
            jitter = node_cfg.get("ramp_j", 0)
            h_range = node_cfg.get("ramp_h", 0)
            s_range = node_cfg.get("ramp_s", 0)
            v_range = node_cfg.get("ramp_v", 0)

            for i, elt in enumerate(ramp.elements):
                e_seed = node_seed + (i * 53)
                random.seed(e_seed)

                # Jitter Position
                if jitter > 0:
                    elt.position = max(0.0, min(1.0, elt.position + random.uniform(-jitter, jitter)))

                # Jitter Color
                r, g, b, a = elt.color
                h, s, v = colorsys.rgb_to_hsv(r, g, b)

                h = (h + random.uniform(-h_range, h_range)) % 1.0
                s = max(0.0, min(1.0, s + random.uniform(-s_range, s_range)))
                v = max(0.0, min(1.0, v + random.uniform(-v_range, v_range)))

                nr, ng, nb = colorsys.hsv_to_rgb(h, s, v)
                elt.color = (nr, ng, nb, a)

        # 2. Handle Sockets
        sockets_cfg = node_cfg.get("sockets", {})
        for i, socket in enumerate(node.inputs):
            s_cfg = sockets_cfg.get(socket.name)
            if not s_cfg or s_cfg.get("locked", False) or socket.is_linked:
                continue

            socket_seed = node_seed + (i * 7919)
            dist = s_cfg.get("dist", "UNIFORM")

            if socket.type == 'VALUE':
                socket.default_value = get_random_value(
                    s_cfg.get("min_f", 0), s_cfg.get("max_f", 1), dist, socket_seed
                )

            elif socket.type == 'VECTOR':
                mode = s_cfg.get("vec_mode", "FREE")
                min_v = s_cfg.get("min_v", [0, 0, 0])
                max_v = s_cfg.get("max_v", [1, 1, 1])

                x = get_random_value(min_v[0], max_v[0], dist, socket_seed + 1)
                if mode == 'UNIFORM':
                    y, z = x, x
                else:
                    y = get_random_value(min_v[1], max_v[1], dist, socket_seed + 2)
                    z = get_random_value(min_v[2], max_v[2], dist, socket_seed + 3)

                if mode == 'SNAP_90':
                    step = math.pi / 2
                    x, y, z = [round(val / step) * step for val in (x, y, z)]
                elif mode == 'INTEGER':
                    x, y, z = round(x), round(y), round(z)

                socket.default_value = (x, y, z)

            elif socket.type == 'RGBA':
                min_hsv = s_cfg.get("min_hsv", [0, 0, 0, 1])
                max_hsv = s_cfg.get("max_hsv", [1, 1, 1, 1])

                h = get_random_value(min_hsv[0], max_hsv[0], dist, socket_seed + 1) % 1.0
                s = get_random_value(min_hsv[1], max_hsv[1], dist, socket_seed + 2)
                v = get_random_value(min_hsv[2], max_hsv[2], dist, socket_seed + 3)
                a = get_random_value(min_hsv[3], max_hsv[3], dist, socket_seed + 4)

                rgb = colorsys.hsv_to_rgb(h, s, v)
                socket.default_value = (*rgb, a)

    material.node_tree.interface_update(bpy.context)


